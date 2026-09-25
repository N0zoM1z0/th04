void near sub_B9F2(void)
{
	uint32_t bonus;
	uint32_t item_penalty;
	random_seed = resident->rand;
	switch(resident->credit_lives) {
	case 1: bonus = 2500; break;
	case 2: bonus = 2000; break;
	case 3: bonus = 1500; break;
	case 4: bonus = 1000; break;
	case 5: bonus = 500;  break;
	case 6: bonus = 0;    break;
	}
	switch(resident->credit_bombs) {
	case 0: bonus += 2500; break;
	case 1: bonus += 1500; break;
	}
	if(resident->turbo_mode) {
		bonus += 2000;
	}
	if(resident->graze) {
		bonus += (resident->graze * 2);
	}
	item_penalty = 1000000UL;
	if(resident->items_spawned != resident->items_collected) {
		if(resident->items_spawned) {
			item_penalty /= resident->items_spawned;
		} else {
			item_penalty = 0;
		}
		item_penalty *= resident->items_collected;
	}
	item_penalty = (1000000UL - item_penalty);
	item_penalty /= 100UL;
	if(item_penalty) {
		bonus += (static_cast<uint32_t>(irand()) % item_penalty);
	}
	bonus *= 100UL;
	if(bonus > 1000000UL) {
		bonus = 1000000UL;
	}
	skill = (skill + bonus);
	graph_fraction_of_million_put(192, 264, bonus);
	graph_putsa_fx(288, 264, 14, aBu_0);
}
