#include "host_joystick_api.hpp"
#include <algorithm>

namespace th04::portable::host_joystick {
namespace {
#ifdef _WIN32
class Platform final:public Device {
public:
    explicit Platform(Api api):api_(api) {
        if(!api.count || !api.caps || !api.position)throw std::invalid_argument("incomplete WinMM joystick API");
    }
    Sample read() override {
        JOYINFOEX position{};position.dwSize=sizeof(position);
        position.dwFlags=JOY_RETURNX|JOY_RETURNY|JOY_RETURNBUTTONS|JOY_RETURNPOVCTS;
        if(id_<0) {
            const auto count=api_.count();
            for(UINT id=0;id<count;++id) {
                JOYCAPSA caps{};
                position={};position.dwSize=sizeof(position);
                position.dwFlags=JOY_RETURNX|JOY_RETURNY|JOY_RETURNBUTTONS|JOY_RETURNPOVCTS;
                if(api_.caps(id,&caps,sizeof(caps))==JOYERR_NOERROR &&
                   api_.position(id,&position)==JOYERR_NOERROR) {
                    id_=id;caps_=caps;break;
                }
            }
            if(id_<0)return {};
        } else if(api_.position(UINT(id_),&position)!=JOYERR_NOERROR) {id_=-1;return {};}
        const auto axis=[](DWORD value,UINT low,UINT high) {
            if(high<=low)return 0;
            const auto bounded=std::max(std::uint64_t(low),std::min(std::uint64_t(high),std::uint64_t(value)));
            return int((bounded-low)*65535/(std::uint64_t(high)-low))-32768;
        };
        auto actions=axis_actions(caps_.wNumAxes>=1?axis(position.dwXpos,caps_.wXmin,caps_.wXmax):0,
                                 caps_.wNumAxes>=2?axis(position.dwYpos,caps_.wYmin,caps_.wYmax):0);
        if((caps_.wCaps&JOYCAPS_HASPOV) && position.dwPOV<36000) {
            constexpr std::uint8_t directions[]{1,9,8,10,2,6,4,5};
            actions|=directions[((position.dwPOV+2250)/4500)%8];
        }
        if(caps_.wNumButtons>=1 && (position.dwButtons&JOY_BUTTON1))actions|=0x20;
        if(caps_.wNumButtons>=2 && (position.dwButtons&JOY_BUTTON2))actions|=0x10;
        return {id_,std::uint8_t(0xff^actions)};
    }
private:
    Api api_;std::int64_t id_=-1;JOYCAPSA caps_{};
};
#else
class Platform final:public Device {
public:
    explicit Platform(Api api):api_(api) {
        if(!api.init || !api.quit || !api.count || !api.open || !api.close || !api.update ||
           !api.attached || !api.identity || !api.axes || !api.hats || !api.buttons ||
           !api.axis || !api.hat || !api.button)throw std::invalid_argument("incomplete SDL joystick API");
        initialized_=api_.init(SDL_INIT_JOYSTICK)==0;
    }
    ~Platform() override {if(handle_)api_.close(handle_);if(initialized_)api_.quit(SDL_INIT_JOYSTICK);}
    Sample read() override {
        if(!initialized_)return {};
        api_.update();
        if(handle_ && !api_.attached(handle_)){api_.close(handle_);handle_=nullptr;}
        if(!handle_) {
            const auto count=api_.count();
            for(int i=0;i<count;++i) {
                handle_=api_.open(i);
                if(!handle_)continue;
                if(api_.attached(handle_) && api_.identity(handle_)>=0)break;
                api_.close(handle_);handle_=nullptr;
            }
            if(!handle_)return {};
        }
        const auto identity=api_.identity(handle_);
        if(identity<0){api_.close(handle_);handle_=nullptr;return {};}
        const auto axes=api_.axes(handle_),buttons=api_.buttons(handle_);
        auto actions=axis_actions(axes>=1?api_.axis(handle_,0):0,axes>=2?api_.axis(handle_,1):0);
        if(api_.hats(handle_)>0) {
            const auto hat=api_.hat(handle_,0);
            actions|=std::uint8_t(((hat&SDL_HAT_UP)?1:0)|((hat&SDL_HAT_DOWN)?2:0)|
                ((hat&SDL_HAT_LEFT)?4:0)|((hat&SDL_HAT_RIGHT)?8:0));
        }
        if(buttons>=1 && api_.button(handle_,0))actions|=0x20;
        if(buttons>=2 && api_.button(handle_,1))actions|=0x10;
        return {identity,std::uint8_t(0xff^actions)};
    }
private:
    Api api_;bool initialized_=false;SDL_Joystick* handle_=nullptr;
};
#endif
} // namespace
std::unique_ptr<Device> platform_device(const Api& api){return std::make_unique<Platform>(api);}
std::unique_ptr<Device> platform_device() {
#ifdef _WIN32
    return platform_device({&joyGetNumDevs,&joyGetDevCapsA,&joyGetPosEx});
#else
    return platform_device({&SDL_InitSubSystem,&SDL_QuitSubSystem,&SDL_NumJoysticks,&SDL_JoystickOpen,
        &SDL_JoystickClose,&SDL_JoystickUpdate,&SDL_JoystickGetAttached,&SDL_JoystickInstanceID,
        &SDL_JoystickNumAxes,&SDL_JoystickNumHats,&SDL_JoystickNumButtons,
        &SDL_JoystickGetAxis,&SDL_JoystickGetHat,&SDL_JoystickGetButton});
#endif
}
} // namespace th04::portable::host_joystick
