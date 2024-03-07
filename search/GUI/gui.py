import tkinter as tk
from tkinter import Button, filedialog
from tkintermapview import TkinterMapView
from search.graph import *
from PIL import Image, ImageTk
import json

class Window:

    def __init__(self):
        win = tk.Tk()

        WIDTH = 1500
        HEIGHT = 1000
        gmap_widget = TkinterMapView(win, width=WIDTH, height=HEIGHT)
        gmap_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        gmap_widget.fit_bounding_box((36.17379613378875, -97.1056278405002), (36.14500140909821, -97.06955381993369))

        win.geometry(f"{WIDTH}x{HEIGHT}")
        win.title("Google Map Viewer")
        win.resizable(False, False)

        graph = Graph()
        marker_list = []
        connection_list = []
        path_dict = {}
        selected = []
        buttons = []

        #load_file = "../../logs/airport_test.json"
        save_file = "../../logs/test.json"

        def load_file():
            filename = filedialog.askopenfilename(initialdir = "../../logs/",
                                          title = "Select a File",
                                          filetypes = (("JSON files",
                                                        "*.json*"),
                                                       ("all files",
                                                        "*.*")))

            if filename is not None:
                with open(filename) as file:
                    data = json.load(file)
                graph = Graph.from_dict(data)

                for node in graph.nodes:
                    new_marker = gmap_widget.set_marker(node.pos[0], node.pos[1], text=node.name, icon=red)
                    marker_list.append(new_marker)

                    neighbors = graph.get_neighbors(node)
                    for neighbor in neighbors:
                        key = frozenset([node.name, neighbor.name])
                        if key not in connection_list:
                            path = gmap_widget.set_path([node.pos, neighbor.pos])
                            path_dict[key] = path
                            connection_list.append(key)

        red = ImageTk.PhotoImage(Image.open("red.png").resize((15, 15)))
        green = ImageTk.PhotoImage(Image.open("green.png").resize((15, 15)))

        self.current_command = None
        default_color = None


        def change_button_colors():
            for btn in buttons:
                if self.current_command == btn.cget("text"):
                    btn.configure(bg="#52f56f")
                else:
                    btn.configure(bg=default_color)

        def toggle_add():
            self.current_command = "Add Nodes"
            change_button_colors()
            gmap_widget.add_left_click_map_command(add_marker_event)
            cancel_connection_event()

        def toggle_connection():
            self.current_command = "Add Connections"
            change_button_colors()
            gmap_widget.add_left_click_map_command(add_connection_event)

        def toggle_remove():
            self.current_command = "Remove Nodes"
            change_button_colors()
            gmap_widget.add_left_click_map_command(remove_node_event)
            cancel_connection_event()

        btn0 = Button(win, text='Load File', command=load_file)
        btn1 = Button(win, text='Add Nodes', command=toggle_add)
        btn2 = Button(win, text='Add Connections', command=toggle_connection)
        btn3 = Button(win, text='Remove Nodes', command=toggle_remove)
        default_color = btn1.cget("bg")
        buttons.append(btn0)
        buttons.append(btn1)
        buttons.append(btn2)
        buttons.append(btn3)

        btn0.grid(row=0, column=0, sticky="N")
        btn1.grid(row=1, column=0, sticky = "N")
        btn2.grid(row=2, column=0, sticky = "N")
        btn3.grid(row=3, column=0, sticky = "N")
        gmap_widget.grid(row=0,column=2, rowspan=100)

        def add_marker_event(coords):
            for marker in marker_list:
                if abs(coords[0] - marker.position[0]) < 0.00005 and abs(coords[1] - marker.position[1]) < 0.00005:
                    return
            text = str(len(marker_list)+1)
            new_marker = gmap_widget.set_marker(coords[0], coords[1], text=text, icon=red)
            graph.add_node(Node(text, (coords[0], coords[1])))
            marker_list.append(new_marker)
            print(f"Added {text}")

        def add_connection_event(coords):
            if not selected:
                for marker in marker_list:
                    if abs(coords[0] - marker.position[0]) < 0.00005 and abs(coords[1] - marker.position[1]) < 0.00005:
                        new_marker = gmap_widget.set_marker(marker.position[0],
                                                            marker.position[1],
                                                            text=marker.text,
                                                            icon=green)
                        marker_list.append(new_marker)
                        marker_list.remove(marker)
                        selected.append(new_marker)
                        marker.delete()
                        print(f"Selected {new_marker.text}")
                        break
            else:
                for marker in marker_list:
                    if abs(coords[0] - marker.position[0]) < 0.00005 and abs(coords[1] - marker.position[1]) < 0.00005:
                        if marker == selected[0]:
                            return
                        else:
                            if frozenset([selected[0].text, marker.text]) not in connection_list:
                                path = gmap_widget.set_path([selected[0].position, marker.position])
                                path_dict[frozenset([selected[0].text, marker.text])] = path
                                connection_list.append(frozenset([selected[0].text, marker.text]))
                                graph.add_edge(graph.get_node_from_name(selected[0].text), graph.get_node_from_name(marker.text))
                                print(f"Added connection {[selected[0].text, marker.text]}")
                                cancel_connection_event()
                                break
                            else:
                                print("Already connected.")


        def remove_node_event(coords):
            for marker in marker_list:
                if abs(coords[0] - marker.position[0]) < 0.00005 and abs(coords[1] - marker.position[1]) < 0.00005:
                    marker_list.remove(marker)
                    graph.remove_node(graph.get_node_from_name(marker.text))
                    print(f"Removed Marker {marker.text}")
                    deletion_list = []
                    for connection in connection_list:
                        nodes = list(connection)
                        if marker.text in nodes:
                            path = path_dict.pop(connection)
                            path.delete()
                            print(f"Removed Connection {nodes}")
                            deletion_list.append(connection)
                    for key in deletion_list:
                        connection_list.remove(key)
                    marker.delete()
                    break

        def cancel_connection_event():
            for select in selected:
                new_marker = gmap_widget.set_marker(select.position[0], select.position[1], text=select.text, icon=red)
                marker_list.remove(select)
                marker_list.append(new_marker)
                select.delete()
                selected.remove(select)

        def on_closing():
            json_dict = graph.to_dict()
            json_obj = json.dumps(json_dict)
            with open(save_file, "w") as outfile:
                outfile.write(json_obj)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        win.mainloop()


Window()
