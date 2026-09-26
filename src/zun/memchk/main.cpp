// TH04 MEMCHK component.
// Tiny-model C++ front end with shared MASTER-compatible DOS helpers.

extern "C" unsigned pascal near DOS_MAXFREE(void);
extern "C" void pascal near DOS_PUTS2(const char near *text);

char mem_msg[] = "空きメインメモリチェック\n\n";
char low_msg[] = "ちょっと足りないかも、もう少し増やしてから起動してね";

int main(void)
{
    unsigned maxfree = DOS_MAXFREE();
    DOS_PUTS2(mem_msg);
    if(maxfree <= 30000U) {
        DOS_PUTS2(low_msg);
        return 255;
    }
    return 0;
}
