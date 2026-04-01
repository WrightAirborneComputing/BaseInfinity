import json
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class CircuitMatrixTool:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Circuit Matrix Tool (Resistors + Voltage Sources)")
        self.root.geometry("1350x860")

        self.nodes = []
        self.resistors = []
        self.vsources = []

        self.node_counter = 1
        self.res_counter = 1
        self.vsrc_counter = 1

        self._build_ui()
        self._load_example()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y")

        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._build_node_panel(left)
        self._build_component_panel(left)
        self._build_actions_panel(left)

        self._build_canvas_panel(right)
        self._build_results_panel(right)

    def _build_node_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Nodes", padding=8)
        frm.pack(fill="x", pady=(0, 8))

        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="Name").pack(side="left")
        self.node_name_var = tk.StringVar(value="N1")
        ttk.Entry(row1, textvariable=self.node_name_var, width=10).pack(side="left", padx=6)
        ttk.Label(row1, text="X").pack(side="left")
        self.node_x_var = tk.StringVar(value="")
        ttk.Entry(row1, textvariable=self.node_x_var, width=7).pack(side="left", padx=6)
        ttk.Label(row1, text="Y").pack(side="left")
        self.node_y_var = tk.StringVar(value="")
        ttk.Entry(row1, textvariable=self.node_y_var, width=7).pack(side="left", padx=6)
        ttk.Button(row1, text="Add Node", command=self.add_node).pack(side="left", padx=(8, 0))

        self.nodes_list = tk.Listbox(frm, height=6, width=48)
        self.nodes_list.pack(fill="x", pady=(8, 0))

    def _build_component_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Components", padding=8)
        frm.pack(fill="x", pady=(0, 8))

        # Resistors
        rfrm = ttk.LabelFrame(frm, text="Resistor", padding=6)
        rfrm.pack(fill="x", pady=(0, 8))
        self.res_name_var = tk.StringVar(value="R1")
        self.res_n1_var = tk.StringVar(value="GND")
        self.res_n2_var = tk.StringVar(value="N1")
        self.res_value_var = tk.StringVar(value="1000")

        ttk.Label(rfrm, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(rfrm, textvariable=self.res_name_var, width=10).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(rfrm, text="Node A").grid(row=1, column=0, sticky="w")
        self.res_n1_combo = ttk.Combobox(rfrm, textvariable=self.res_n1_var, width=10, state="readonly")
        self.res_n1_combo.grid(row=1, column=1, padx=4, pady=2)
        ttk.Label(rfrm, text="Node B").grid(row=2, column=0, sticky="w")
        self.res_n2_combo = ttk.Combobox(rfrm, textvariable=self.res_n2_var, width=10, state="readonly")
        self.res_n2_combo.grid(row=2, column=1, padx=4, pady=2)
        ttk.Label(rfrm, text="Resistance (Ohm)").grid(row=3, column=0, sticky="w")
        ttk.Entry(rfrm, textvariable=self.res_value_var, width=12).grid(row=3, column=1, padx=4, pady=2)
        ttk.Button(rfrm, text="Add Resistor", command=self.add_resistor).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        # Voltage sources
        vfrm = ttk.LabelFrame(frm, text="Voltage Source", padding=6)
        vfrm.pack(fill="x")
        self.v_name_var = tk.StringVar(value="V1")
        self.v_pos_var = tk.StringVar(value="N1")
        self.v_neg_var = tk.StringVar(value="GND")
        self.v_value_var = tk.StringVar(value="10")

        ttk.Label(vfrm, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(vfrm, textvariable=self.v_name_var, width=10).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(vfrm, text="Positive Node").grid(row=1, column=0, sticky="w")
        self.v_pos_combo = ttk.Combobox(vfrm, textvariable=self.v_pos_var, width=10, state="readonly")
        self.v_pos_combo.grid(row=1, column=1, padx=4, pady=2)
        ttk.Label(vfrm, text="Negative Node").grid(row=2, column=0, sticky="w")
        self.v_neg_combo = ttk.Combobox(vfrm, textvariable=self.v_neg_var, width=10, state="readonly")
        self.v_neg_combo.grid(row=2, column=1, padx=4, pady=2)
        ttk.Label(vfrm, text="Voltage (V)").grid(row=3, column=0, sticky="w")
        ttk.Entry(vfrm, textvariable=self.v_value_var, width=12).grid(row=3, column=1, padx=4, pady=2)
        ttk.Button(vfrm, text="Add Voltage Source", command=self.add_vsource).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        self.components_list = tk.Listbox(frm, height=9, width=48)
        self.components_list.pack(fill="x", pady=(8, 0))

    def _build_actions_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Actions", padding=8)
        frm.pack(fill="x")

        ttk.Button(frm, text="Generate Matrix", command=self.generate_matrix).pack(fill="x", pady=2)
        ttk.Button(frm, text="Auto Layout Nodes", command=self.auto_layout_nodes).pack(fill="x", pady=2)
        ttk.Button(frm, text="Delete Selected", command=self.delete_selected).pack(fill="x", pady=2)
        ttk.Button(frm, text="Clear All", command=self.clear_all).pack(fill="x", pady=2)
        ttk.Button(frm, text="Load JSON", command=self.load_json).pack(fill="x", pady=2)
        ttk.Button(frm, text="Save JSON", command=self.save_json).pack(fill="x", pady=2)

        note = (
            "Uses Modified Nodal Analysis (MNA).\n"
            "Unknowns are node voltages (except GND) and current through each voltage source.\n"
            "Current sources are not included in this version."
        )
        ttk.Label(frm, text=note, wraplength=320, justify="left").pack(fill="x", pady=(8, 0))

    def _build_canvas_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Circuit Graph", padding=8)
        frm.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(frm, bg="white", height=420)
        self.canvas.pack(fill="both", expand=True)

    def _build_results_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Matrices and Solution", padding=8)
        frm.pack(fill="both", expand=True, pady=(8, 0))

        self.results_text = tk.Text(frm, wrap="none", height=18, font=("Consolas", 10))
        xscroll = ttk.Scrollbar(frm, orient="horizontal", command=self.results_text.xview)
        yscroll = ttk.Scrollbar(frm, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)

        self.results_text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        frm.rowconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)

    def _load_example(self):
        self.nodes = [
            {"name": "GND", "x": 120, "y": 200},
            {"name": "N1", "x": 320, "y": 120},
            {"name": "N2", "x": 560, "y": 200},
        ]
        self.resistors = [
            {"name": "R1", "n1": "N1", "n2": "GND", "value": 1000.0},
            {"name": "R2", "n1": "N1", "n2": "N2", "value": 2000.0},
            {"name": "R3", "n1": "N2", "n2": "GND", "value": 1500.0},
        ]
        self.vsources = [
            {"name": "V1", "p": "N1", "n": "GND", "value": 10.0},
        ]
        self.node_counter = 3
        self.res_counter = 4
        self.vsrc_counter = 2
        self.refresh_all()
        self.generate_matrix()

    def refresh_all(self):
        self.refresh_node_options()
        self.refresh_lists()
        self.redraw_canvas()

    def refresh_node_options(self):
        names = [n["name"] for n in self.nodes]
        self.res_n1_combo["values"] = names
        self.res_n2_combo["values"] = names
        self.v_pos_combo["values"] = names
        self.v_neg_combo["values"] = names

        if "GND" in names:
            if not self.res_n1_var.get() in names:
                self.res_n1_var.set("GND")
            if not self.v_neg_var.get() in names:
                self.v_neg_var.set("GND")
        if len(names) > 1:
            default_non_ground = next((name for name in names if name != "GND"), names[0])
            if self.res_n2_var.get() not in names:
                self.res_n2_var.set(default_non_ground)
            if self.v_pos_var.get() not in names:
                self.v_pos_var.set(default_non_ground)

    def refresh_lists(self):
        self.nodes_list.delete(0, "end")
        for node in self.nodes:
            self.nodes_list.insert("end", f'{node["name"]}: ({int(node["x"])}, {int(node["y"])})')

        self.components_list.delete(0, "end")
        for r in self.resistors:
            self.components_list.insert("end", f'{r["name"]}: {r["n1"]} -- {r["n2"]}   {r["value"]} Ohm')
        for v in self.vsources:
            self.components_list.insert("end", f'{v["name"]}: {v["p"]} (+) , {v["n"]} (-)   {v["value"]} V')

    def find_node(self, name: str):
        for node in self.nodes:
            if node["name"] == name:
                return node
        return None

    def add_node(self):
        name = self.node_name_var.get().strip()
        if not name:
            messagebox.showerror("Invalid node", "Please enter a node name.")
            return
        if self.find_node(name) is not None:
            messagebox.showerror("Duplicate node", f"Node '{name}' already exists.")
            return

        try:
            x = float(self.node_x_var.get()) if self.node_x_var.get().strip() else None
            y = float(self.node_y_var.get()) if self.node_y_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Invalid coordinates", "X and Y must be numbers.")
            return

        if x is None or y is None:
            count = max(1, len(self.nodes))
            angle = 2 * math.pi * (len(self.nodes) / count)
            x = 200 + 140 * math.cos(angle)
            y = 180 + 120 * math.sin(angle)

        self.nodes.append({"name": name, "x": x, "y": y})
        self.node_counter += 1
        self.node_name_var.set(f"N{self.node_counter}")
        self.node_x_var.set("")
        self.node_y_var.set("")
        self.refresh_all()

    def add_resistor(self):
        name = self.res_name_var.get().strip()
        n1 = self.res_n1_var.get().strip()
        n2 = self.res_n2_var.get().strip()

        if not name:
            messagebox.showerror("Invalid resistor", "Please enter a resistor name.")
            return
        if self._component_name_exists(name):
            messagebox.showerror("Duplicate name", f"A component named '{name}' already exists.")
            return
        if self.find_node(n1) is None or self.find_node(n2) is None:
            messagebox.showerror("Invalid resistor", "Both nodes must exist.")
            return
        if n1 == n2:
            messagebox.showerror("Invalid resistor", "A resistor must connect two different nodes.")
            return

        text = self.res_value_var.get().strip().lower()
        try:
            if text in ["inf", "infinite", "infinity"]:
                value = float("inf")
            else:
                value = float(text)
        except ValueError:
            messagebox.showerror("Invalid resistor", "Resistance must be numeric or 'inf'.")
            return
        # Allow zero and infinite resistance
        # Zero = short circuit, inf = open circuit
        # So we only reject negative values
        if value < 0:
            messagebox.showerror("Invalid resistor", "Resistance must not be negative.")
            return

        self.resistors.append({"name": name, "n1": n1, "n2": n2, "value": value})
        self.res_counter += 1
        self.res_name_var.set(f"R{self.res_counter}")
        self.refresh_all()

    def add_vsource(self):
        name = self.v_name_var.get().strip()
        p = self.v_pos_var.get().strip()
        n = self.v_neg_var.get().strip()

        if not name:
            messagebox.showerror("Invalid voltage source", "Please enter a source name.")
            return
        if self._component_name_exists(name):
            messagebox.showerror("Duplicate name", f"A component named '{name}' already exists.")
            return
        if self.find_node(p) is None or self.find_node(n) is None:
            messagebox.showerror("Invalid voltage source", "Both nodes must exist.")
            return
        if p == n:
            messagebox.showerror("Invalid voltage source", "Positive and negative nodes must differ.")
            return

        try:
            value = float(self.v_value_var.get())
        except ValueError:
            messagebox.showerror("Invalid voltage source", "Voltage must be numeric.")
            return

        self.vsources.append({"name": name, "p": p, "n": n, "value": value})
        self.vsrc_counter += 1
        self.v_name_var.set(f"V{self.vsrc_counter}")
        self.refresh_all()

    def _component_name_exists(self, name: str) -> bool:
        return any(c["name"] == name for c in self.resistors) or any(c["name"] == name for c in self.vsources)

    def delete_selected(self):
        node_idx = self.nodes_list.curselection()
        comp_idx = self.components_list.curselection()

        if node_idx:
            idx = node_idx[0]
            node_name = self.nodes[idx]["name"]
            if node_name == "GND":
                messagebox.showerror("Cannot delete", "Ground node cannot be deleted in this version.")
                return

            for r in self.resistors:
                if r["n1"] == node_name or r["n2"] == node_name:
                    messagebox.showerror("Cannot delete", f"Node '{node_name}' is still used by {r['name']}.")
                    return
            for v in self.vsources:
                if v["p"] == node_name or v["n"] == node_name:
                    messagebox.showerror("Cannot delete", f"Node '{node_name}' is still used by {v['name']}.")
                    return

            del self.nodes[idx]
            self.refresh_all()
            return

        if comp_idx:
            idx = comp_idx[0]
            if idx < len(self.resistors):
                del self.resistors[idx]
            else:
                del self.vsources[idx - len(self.resistors)]
            self.refresh_all()
            return

        messagebox.showinfo("Nothing selected", "Select a node or component to delete.")

    def clear_all(self):
        if not messagebox.askyesno("Clear all", "Remove all nodes and components and start again?"):
            return
        self.nodes = [{"name": "GND", "x": 120, "y": 200}]
        self.resistors = []
        self.vsources = []
        self.node_counter = 1
        self.res_counter = 1
        self.vsrc_counter = 1
        self.node_name_var.set("N1")
        self.res_name_var.set("R1")
        self.v_name_var.set("V1")
        self.refresh_all()
        self.results_text.delete("1.0", "end")

    def to_dict(self):
        def encode_resistor_value(value):
            if isinstance(value, float) and math.isinf(value):
                return "inf"
            return value

        return {
            "format": "circuit_matrix_tool",
            "version": 1,
            "nodes": [
                {"name": n["name"], "x": n["x"], "y": n["y"]}
                for n in self.nodes
            ],
            "resistors": [
                {
                    "name": r["name"],
                    "n1": r["n1"],
                    "n2": r["n2"],
                    "value": encode_resistor_value(r["value"]),
                }
                for r in self.resistors
            ],
            "voltage_sources": [
                {
                    "name": v["name"],
                    "p": v["p"],
                    "n": v["n"],
                    "value": v["value"],
                }
                for v in self.vsources
            ],
        }

    def load_from_dict(self, data):
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object.")

        nodes = data.get("nodes")
        resistors = data.get("resistors", [])
        voltage_sources = data.get("voltage_sources", [])

        if not isinstance(nodes, list) or len(nodes) == 0:
            raise ValueError("JSON must contain a non-empty 'nodes' array.")

        new_nodes = []
        seen_node_names = set()
        for node in nodes:
            if not isinstance(node, dict):
                raise ValueError("Each node must be an object.")
            name = str(node.get("name", "")).strip()
            if not name:
                raise ValueError("Each node must have a name.")
            if name in seen_node_names:
                raise ValueError(f"Duplicate node name: {name}")
            seen_node_names.add(name)
            try:
                x = float(node.get("x", 0))
                y = float(node.get("y", 0))
            except Exception:
                raise ValueError(f"Node '{name}' has invalid x/y coordinates.")
            new_nodes.append({"name": name, "x": x, "y": y})

        if "GND" not in seen_node_names:
            raise ValueError("JSON must include a node named 'GND'.")

        new_resistors = []
        comp_names = set()
        for resistor in resistors:
            if not isinstance(resistor, dict):
                raise ValueError("Each resistor must be an object.")
            name = str(resistor.get("name", "")).strip()
            n1 = str(resistor.get("n1", "")).strip()
            n2 = str(resistor.get("n2", "")).strip()
            raw_value = resistor.get("value")
            if not name or not n1 or not n2:
                raise ValueError("Each resistor must have name, n1, and n2.")
            if name in comp_names:
                raise ValueError(f"Duplicate component name: {name}")
            if n1 not in seen_node_names or n2 not in seen_node_names:
                raise ValueError(f"Resistor '{name}' references an unknown node.")
            if n1 == n2:
                raise ValueError(f"Resistor '{name}' must connect two different nodes.")
            if isinstance(raw_value, str) and raw_value.strip().lower() in ["inf", "infinite", "infinity"]:
                value = float("inf")
            else:
                try:
                    value = float(raw_value)
                except Exception:
                    raise ValueError(f"Resistor '{name}' has invalid value.")
            if value < 0:
                raise ValueError(f"Resistor '{name}' must not be negative.")
            comp_names.add(name)
            new_resistors.append({"name": name, "n1": n1, "n2": n2, "value": value})

        new_vsources = []
        for source in voltage_sources:
            if not isinstance(source, dict):
                raise ValueError("Each voltage source must be an object.")
            name = str(source.get("name", "")).strip()
            p = str(source.get("p", "")).strip()
            n = str(source.get("n", "")).strip()
            if not name or not p or not n:
                raise ValueError("Each voltage source must have name, p, and n.")
            if name in comp_names:
                raise ValueError(f"Duplicate component name: {name}")
            if p not in seen_node_names or n not in seen_node_names:
                raise ValueError(f"Voltage source '{name}' references an unknown node.")
            if p == n:
                raise ValueError(f"Voltage source '{name}' must connect two different nodes.")
            try:
                value = float(source.get("value"))
            except Exception:
                raise ValueError(f"Voltage source '{name}' has invalid value.")
            comp_names.add(name)
            new_vsources.append({"name": name, "p": p, "n": n, "value": value})

        self.nodes = new_nodes
        self.resistors = new_resistors
        self.vsources = new_vsources

        node_numbers = [
            int(n["name"][1:]) for n in self.nodes
            if n["name"].startswith("N") and n["name"][1:].isdigit()
        ]
        res_numbers = [
            int(r["name"][1:]) for r in self.resistors
            if r["name"].startswith("R") and r["name"][1:].isdigit()
        ]
        vsrc_numbers = [
            int(v["name"][1:]) for v in self.vsources
            if v["name"].startswith("V") and v["name"][1:].isdigit()
        ]

        self.node_counter = (max(node_numbers) + 1) if node_numbers else 1
        self.res_counter = (max(res_numbers) + 1) if res_numbers else 1
        self.vsrc_counter = (max(vsrc_numbers) + 1) if vsrc_numbers else 1

        self.node_name_var.set(f"N{self.node_counter}")
        self.res_name_var.set(f"R{self.res_counter}")
        self.v_name_var.set(f"V{self.vsrc_counter}")
        self.refresh_all()

    def save_json(self):
        path = filedialog.asksaveasfilename(
            title="Save circuit JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as exc:
            messagebox.showerror("Save failed", f"Could not save JSON file:{exc}")
            return
        messagebox.showinfo("Saved", f"Circuit saved to:{path}")

    def load_json(self):
        path = filedialog.askopenfilename(
            title="Load circuit JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.load_from_dict(data)
            self.results_text.delete("1.0", "end")
            self.generate_matrix()
        except Exception as exc:
            messagebox.showerror("Load failed", f"Could not load JSON file:{exc}")

    def auto_layout_nodes(self):
        if not self.nodes:
            return
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 420)
        cx = width / 2
        cy = height / 2
        radius = min(width, height) * 0.32

        movable = [n for n in self.nodes if n["name"] != "GND"]
        ground = self.find_node("GND")
        if ground is not None:
            ground["x"] = cx - radius - 80
            ground["y"] = cy

        count = max(1, len(movable))
        for i, node in enumerate(movable):
            angle = -math.pi / 2 + (2 * math.pi * i / count)
            node["x"] = cx + radius * math.cos(angle)
            node["y"] = cy + radius * math.sin(angle)

        self.refresh_all()

    def redraw_canvas(self):
        self.canvas.delete("all")

        for resistor in self.resistors:
            self._draw_component_line(resistor["n1"], resistor["n2"], resistor["name"], f'{resistor["value"]} Ω', "#1f77b4")

        for source in self.vsources:
            self._draw_component_line(source["p"], source["n"], source["name"], f'{source["value"]} V', "#d62728", polarity=True)

        for node in self.nodes:
            x, y = node["x"], node["y"]
            r = 12
            fill = "#2ca02c" if node["name"] == "GND" else "#444444"
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="black")
            self.canvas.create_text(x, y - 20, text=node["name"], font=("Arial", 10, "bold"))

    def _draw_component_line(self, n1_name, n2_name, label1, label2, color, polarity=False):
        n1 = self.find_node(n1_name)
        n2 = self.find_node(n2_name)
        if n1 is None or n2 is None:
            return

        x1, y1 = n1["x"], n1["y"]
        x2, y2 = n2["x"], n2["y"]
        self.canvas.create_line(x1, y1, x2, y2, width=3, fill=color)

        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length

        self.canvas.create_rectangle(mx - 42, my - 18, mx + 42, my + 18, fill="white", outline=color)
        self.canvas.create_text(mx, my - 6, text=label1, font=("Arial", 9, "bold"), fill=color)
        self.canvas.create_text(mx, my + 8, text=label2, font=("Arial", 9), fill=color)

        if polarity:
            self.canvas.create_text(x1 + nx * 16, y1 + ny * 16, text="+", fill=color, font=("Arial", 12, "bold"))
            self.canvas.create_text(x2 + nx * 16, y2 + ny * 16, text="-", fill=color, font=("Arial", 12, "bold"))

    def generate_matrix(self):
        try:
            result = self.build_mna_system()
        except ValueError as exc:
            messagebox.showerror("Cannot generate matrix", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Error", f"Unexpected error: {exc}")
            return

        self.show_result(result)

    def build_mna_system(self):
        if self.find_node("GND") is None:
            raise ValueError("A ground node named 'GND' is required.")
        if len(self.nodes) < 2:
            raise ValueError("Add at least one non-ground node.")

        node_names = [n["name"] for n in self.nodes if n["name"] != "GND"]
        node_index = {name: i for i, name in enumerate(node_names)}
        m = len(node_names)
        k = len(self.vsources)

        G = [[0.0 for _ in range(m)] for _ in range(m)]
        B = [[0.0 for _ in range(k)] for _ in range(m)]
        I = [0.0 for _ in range(m)]
        E = [0.0 for _ in range(k)]

        def stamp_conductance(n1, n2, g):
            if n1 != "GND":
                i = node_index[n1]
                G[i][i] += g
            if n2 != "GND":
                j = node_index[n2]
                G[j][j] += g
            if n1 != "GND" and n2 != "GND":
                i = node_index[n1]
                j = node_index[n2]
                G[i][j] -= g
                G[j][i] -= g

        for resistor in self.resistors:
            val = resistor["value"]

            # Handle infinite resistance (open circuit)
            if isinstance(val, float) and math.isinf(val):
                continue  # no connection
            g = 1.0 / val

            stamp_conductance(resistor["n1"], resistor["n2"], g)

        for col, source in enumerate(self.vsources):
            p = source["p"]
            n = source["n"]
            if p != "GND":
                B[node_index[p]][col] += 1.0
            if n != "GND":
                B[node_index[n]][col] -= 1.0
            E[col] = source["value"]

        # Assemble A = [[G, B], [B^T, 0]]
        size = m + k
        A = [[0.0 for _ in range(size)] for _ in range(size)]
        z = [0.0 for _ in range(size)]

        for r in range(m):
            for c in range(m):
                A[r][c] = G[r][c]
        for r in range(m):
            for c in range(k):
                A[r][m + c] = B[r][c]
        for r in range(k):
            for c in range(m):
                A[m + r][c] = B[c][r]

        for i in range(m):
            z[i] = I[i]
        for i in range(k):
            z[m + i] = E[i]
        solution = self.solve_linear_system(A, z)

        node_voltages = {"GND": 0.0}
        for i, name in enumerate(node_names):
            node_voltages[name] = solution[i]

        resistor_flows = []
        for resistor in self.resistors:
            n1 = resistor["n1"]
            n2 = resistor["n2"]
            val = resistor["value"]
            vdrop = node_voltages[n1] - node_voltages[n2]
            if isinstance(val, float) and math.isinf(val):
                current = 0.0
            else:
                current = vdrop / val

            resistor_flows.append({
                "name": resistor["name"],
                "from_node": n1,
                "to_node": n2,
                "resistance": val,
                "voltage_drop": vdrop,
                "current": current,
            })

        return {
            "node_names": node_names,
            "vsource_names": [v["name"] for v in self.vsources],
            "G": G,
            "B": B,
            "A": A,
            "z": z,
            "x": solution,
            "node_voltages": node_voltages,
            "resistor_flows": resistor_flows,
        }

    def solve_linear_system(self, A, b):
        n = len(A)
        M = [row[:] + [bval] for row, bval in zip(A, b)]

        for col in range(n):
            pivot_row = max(range(col, n), key=lambda r: abs(M[r][col]))
            pivot_val = M[pivot_row][col]
            if abs(pivot_val) < 1e-12:
                raise ValueError(
                    "The matrix is singular. The circuit may be floating, inconsistent, or missing a valid ground reference."
                )

            if pivot_row != col:
                M[col], M[pivot_row] = M[pivot_row], M[col]

            pivot = M[col][col]
            for j in range(col, n + 1):
                M[col][j] /= pivot

            for r in range(n):
                if r == col:
                    continue
                factor = M[r][col]
                if abs(factor) < 1e-15:
                    continue
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]

        return [M[i][n] for i in range(n)]

    def show_result(self, result):
        self.results_text.delete("1.0", "end")

        node_names = result["node_names"]
        vsource_names = result["vsource_names"]

        unknowns = [f"V({name})" for name in node_names] + [f"I({name})" for name in vsource_names]

        self._append("Unknown vector x:\n")
        self._append("  [ " + ", ".join(unknowns) + " ]^T\n\n")

        self._append("G matrix:\n")
        self._append(self.format_matrix(result["G"]) + "\n\n")

        self._append("B matrix:\n")
        self._append(self.format_matrix(result["B"]) + "\n\n")

        self._append("Full MNA matrix A:\n")
        self._append(self.format_matrix(result["A"]) + "\n\n")

        self._append("Right-hand side z:\n")
        self._append(self.format_vector(result["z"]) + "\n\n")

        self._append("Solution x:\n")
        self._append(self.format_vector(result["x"]) + "\n\n")
        self._append("Named results:")
        self._append("\n")
        for name, value in zip(unknowns, result["x"]):
            unit = "V" if name.startswith("V(") else "A"
            self._append(f"  {name} = {value:.6g} {unit}")
        # for
        self._append("\n")

        self._append("Resistor flows (positive from Node A to Node B):")
        self._append("\n")
        for flow in result["resistor_flows"]:
            resistance = flow["resistance"]
            if isinstance(resistance, float) and math.isinf(resistance):
                resistance_text = "inf"
            else:
                resistance_text = f"{resistance:.6g}"
            self._append(
                f"  {flow['name']}: I = {flow['current']:.6g} A, "
                f"Vdrop = {flow['voltage_drop']:.6g} V, "
                f"R = {resistance_text} Ohm, "
                f"direction {flow['from_node']} -> {flow['to_node']}")
            self._append("\n")
        # for
        self._append("\n")

    def _append(self, text: str):
        self.results_text.insert("end", text)

    @staticmethod
    def format_matrix(M):
        if not M:
            return "[ ]"
        lines = []
        for row in M:
            lines.append("[ " + "  ".join(f"{val:10.6g}" for val in row) + " ]")
        return "\n".join(lines)

    @staticmethod
    def format_vector(v):
        return "[ " + "  ".join(f"{val:10.6g}" for val in v) + " ]^T"


def main():
    root = tk.Tk()
    try:
        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    app = CircuitMatrixTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
