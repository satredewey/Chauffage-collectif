source venv/bin/activate

clear

python main.py \
  --height 3 \
  --width 4 \
  --pixel_size 100 \
  --do_auto_resize_pixels True \
  --iterations_per_cycle 200000 \
  --max_iteration 5 \
  --do_wait_time False \
  --wait_time 2 \
  --do_limit_fps False \
  --fps 5 \
  --do_ident True \
  --ident_size_spaces 4 \
  --do_save_data False \
  --data_save_name "data.json" \
  --do_display_percentage True \
  --percentage_precision 2 \
  --do_gray_colors False \
  --do_display_temp True \
  --display_temp_precision 2 \
  --display_max_temp 255 \
  --display_min_temp 0 \
  --do_limit_display_fps_to_screen_fps True \
  --display_fps 60 \
  --do_display True \
  --load_grid_from_file "None"

read -p "Appuie sur Entrée pour fermer..."