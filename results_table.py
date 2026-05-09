def fill_results_table(tree, results):

    for row in tree.get_children():
        tree.delete(row)

    if not results:
        return


    for p in results:
        tree.insert("", "end", values=(
            p['id'],
            p['at'],
            p['bt'],
            p['ct'],
            p['tat'],
            p['wt'],
            p['rt']
        ))


    n = len(results)
    avg_tat = sum(p['tat'] for p in results) / n
    avg_wt  = sum(p['wt']  for p in results) / n
    avg_rt  = sum(p['rt']  for p in results) / n


    tree.insert("", "end", values=(
        "Avg",
        "",   
        "",   
        "",   
        f"{avg_tat:.2f}",
        f"{avg_wt:.2f}",
        f"{avg_rt:.2f}"
    ), tags=("average",))


    tree.tag_configure("average", font=("Arial", 10, "bold"))