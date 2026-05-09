def draw_gantt(canvas, gantt_segments, title):

    canvas.delete("all")

    if not gantt_segments:
        canvas.create_text(200, 30, text=title + "\n(No data)", anchor="n")
        return


    left_margin = 60      
    top_margin = 40       
    bar_height = 40
    bar_gap = 5
    time_scale = 40       


    max_time = max(start + dur for _, start, dur in gantt_segments)
    canvas_width = left_margin + max_time * time_scale + 20
    canvas_height = top_margin + bar_height + 40
    canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))


    canvas.create_text(canvas_width / 2, 15, text=title, anchor="n",
                       font=("Arial", 12, "bold"))



    colour_list = [
        "#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA",
        "#E8BAFF", "#FFD9BA", "#B3E5FC", "#C8E6C9",
        "#FFE082", "#CE93D8", "#80DEEA", "#F48FB1",
        "#A5D6A7", "#EF9A9A", "#90CAF9", "#FFF59D"
    ]

    def get_colour(label):

        if label == "Idle":
            return "#D3D3D3"

        if isinstance(label, int):
            idx = label % len(colour_list)
            return colour_list[idx]

        return "#FFFFFF"


    for label, start, dur in gantt_segments:
        x1 = left_margin + start * time_scale
        x2 = x1 + dur * time_scale
        y1 = top_margin
        y2 = y1 + bar_height

        colour = get_colour(label)
        canvas.create_rectangle(x1, y1, x2, y2, fill=colour, outline="black")


        if dur * time_scale > 20:
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                               text=str(label), font=("Arial", 10, "bold"))


        canvas.create_text(x1, y2 + 12, text=str(start), anchor="n",
                           font=("Arial", 8))


    final_time = max_time
    x_final = left_margin + final_time * time_scale
    canvas.create_text(x_final, top_margin + bar_height + 12,
                       text=str(final_time), anchor="n", font=("Arial", 8))


    canvas.config(width=canvas_width, height=canvas_height)