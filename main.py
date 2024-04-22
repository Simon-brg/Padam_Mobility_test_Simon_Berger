from input import parse_cmd_line, parse_file
from graph import Graph

def main():
    in_file, plot_graph = parse_cmd_line()
    vertices, edges = parse_file(in_file)
    print(f"#E={len(edges)}, #V={len(vertices)}")
    graph = Graph(vertices, edges)
    if plot_graph:
        graph.plot()

#C:\Users\HP\AppData\Local\Programs\Python\Python312\python.exe "C:/Users/HP/OneDrive/Documents/Documents_importants/professionnel/Test_Padam_Mobility/main.py" -i "C:/Users/HP/OneDrive/Documents/Documents_importants/professionnel/Test_Padam_Mobility/hard_to_choose.txt" -p


if __name__ == "__main__":
    main()