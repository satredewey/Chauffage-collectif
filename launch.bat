call "venv/Scripts/activate.bat"

cls

python main.py ^
--height 3 ^
--width 4 ^
--pixel_size 25 ^
--do_auto_resize_pixels True ^
--iternations_per_cycle 50 ^
--max_iteration 1 ^
--do_wait_time True ^
--wait_time 2 ^
--do_limit_fps True ^
--fps 5 ^
--do_ident True ^
--ident_size_spaces 4 ^
--data_save_name "data.json" ^
--do_display_percentage True ^
--percentage_precision 2 ^
--do_gray_colors False ^
--do_display_temp True ^
--display_temp_precision 2 ^
--display_max_temp 255 ^
--display_min_temp 0 ^
--load_data_from_file True ^
--data_load_name "default_state.json"