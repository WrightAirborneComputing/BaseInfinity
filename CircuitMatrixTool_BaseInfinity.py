import json
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ---- BaseInfinity numeric system ----
EPS = 1e-12
MAX_EXPONENT = 5
EXPONENTS = list(range(MAX_EXPONENT, -MAX_EXPONENT - 1, -1))

_arithPrintEnabled = False
_truncPrintEnabled = True
_badMatrixPrintEnabled = True

class Column:

    def __init__(self, infPower, mantissa):
        self.mantissa = float(mantissa)
        self.exp = int(infPower)
    # def

    def Compare(self,value):
        return self.mantissa == value
    # def

    def IsZero(self):
        return self.Compare(0.0)
    # def

    def IsNearZero(self):
        return math.fabs(self.mantissa) < 0.001 # i.e. .3f prints 0.000
    # def

    def Text(self):
        if(self.IsZero()):
            return "Zero"
        elif(self.IsNearZero()):
            return "NearZero"
        else:
            return "%.3f" % self.mantissa
        # if
    # def

# class

class Number:

    def __init__(self, *args):

        # Create the columns for all requested infinity-powers
        self.column = {e: Column(e, 0.0) for e in EXPONENTS}

        if len(args) == 1:
            self.column[0].mantissa = float(args[0])
        elif len(args) == 3:
            self.column[ 1].mantissa = float(args[0])
            self.column[ 0].mantissa = float(args[1])
            self.column[-1].mantissa = float(args[2])
        elif len(args) == 5:
            self.column[ 2].mantissa = float(args[0])
            self.column[ 1].mantissa = float(args[1])
            self.column[ 0].mantissa = float(args[2])
            self.column[-1].mantissa = float(args[3])
            self.column[-2].mantissa = float(args[4])
        else:
            raise ValueError("Expected 1,3,5 arguments")
        # if

        # Truncation flag
        self.truncated = False

    # def

    @staticmethod
    def FromColumns(col_dict):
        out = Number(0.0)
        for exp, value in col_dict.items():
            if exp in out.column:
                out.column[exp].mantissa = float(value)
            else:
                if not IsZero(value):
                    print("Warning: constructor ignored exponent %d outside supported range" % exp)
                    out.truncated = True
                # if
            # if
        # for
        return out
    # def

    def Clone(self):
        result = Number.FromColumns({e: self.column[e].mantissa for e in EXPONENTS})
        result.truncated = self.truncated
        return result
    # def

    def Clean(self):
        for e in EXPONENTS:
            if self.column[e].IsZero():
                self.column[e].mantissa = 0.0
            # if
        # for

        return self
    # def

    def Round(self):
        self.Clean()

        # Find the first negative exponent column that is exactly zero,
        # scanning from -1, -2, -3, ... toward the right.
        first_zero_neg_exp = None
        for e in EXPONENTS:
            if e < 0 and self.column[e].IsZero():
                first_zero_neg_exp = e
                break
            # if
        # for

        # Zero all columns to the right of that one
        # (i.e. with more-negative exponents).
        if first_zero_neg_exp is not None:
            for e in EXPONENTS:
                if e < first_zero_neg_exp:
                    self.column[e].mantissa = 0.0
                # if
            # for
        # if

        return self
    # def

    def WarnAndTruncate(self, exp, mantissa, context):
        if not IsZero(mantissa):
            print("Warning: %s produced exponent %d outside supported range; truncating term %g*n^%d" %
                  (context, exp, mantissa, exp))
        # if
    # def

    def IsTrueZero(self):
        for e in EXPONENTS:
            if not self.column[e].IsZero():
                return False
            # if
        # for
        return True
    # def

    def IsUnitZero(self):
        self.Clean()

        for e in EXPONENTS:
            if e == -1:
                if not self.column[e].Compare(1.0):
                    return False
                # if
            else:
                if not self.column[e].IsZero():
                    return False
                # if
            # if
        # for

        return True
    # def

    def IsUnitInfinity(self):
        self.Clean()

        for e in EXPONENTS:
            if e == 1:
                if not self.column[e].Compare(1.0):
                    return False
                # if
            else:
                if not self.column[e].IsZero():
                    return False
                # if
            # if
        # for

        return True
    # def

    def LeadingExp(self):
        for e in EXPONENTS:
            if not self.column[e].IsZero():
                return e
            # if
        # for
        return None
    # def

    def TrailingExp(self):
        for e in reversed(EXPONENTS):
            if not self.column[e].IsZero():
                return e
            # if
        # for
        return None
    # def

    def Text(self):
        self.Clean()

        if self.IsTrueZero():
            return "TrueZero"
        # if

        if self.IsUnitZero():
            return "UnitZero"
        # if

        if self.IsUnitInfinity():
            return "UnitInfinity"
        # if

        # Find all non-zero exponents
        used = [exp for exp in EXPONENTS if not self.column[exp].IsZero()]

        # Determine symmetric range around 0
        k = max(abs(min(used)), abs(max(used)))

        # Determine whether nonzero exponents exist
        has_nonzero_exp = any(exp != 0 for exp in used)

        # Build symmetric list (only within supported EXPONENTS)
        values = []

        # Display each col
        for exp in EXPONENTS:
            if abs(exp) <= k:
                value_text = self.column[exp].Text()

                # Highlight zero-power column only when
                # other exponents are present
                if (exp == 0) and has_nonzero_exp:
                    values.append("*" + value_text + "*")
                else:
                    values.append(value_text)
                # if
            # if

        # for

        return "[" + ",".join(values) + "]"
    # def

    def Real(self):
        lead = self.LeadingExp()

        # TrueZero
        if lead is None:
            return 0.0
        # Infinities in the value
        elif lead > 0:
            return float('inf')
        # Only real and and 1/inf's - discard 1/inf's
        else:
            return self.column[0].mantissa
        # if
    # def

    def __add__(self, operand):
        result = Number(0.0)
        result.truncated = self.truncated or operand.truncated
        for i in EXPONENTS:
            result.column[i].mantissa = self.column[i].mantissa + operand.column[i].mantissa
        # for
        result.Clean()
        if _arithPrintEnabled: print("%s + %s = %s" % (self.Text(), operand.Text(), result.Text()))
        return result
    # def

    def __sub__(self, operand):
        result = Number(0.0)
        result.truncated = self.truncated or operand.truncated
        for i in EXPONENTS:
            result.column[i].mantissa = self.column[i].mantissa - operand.column[i].mantissa
        # for
        result.Clean()
        if _arithPrintEnabled: print("%s - %s = %s" % (self.Text(), operand.Text(), result.Text()))
        return result
    # def

    def __mul__(self, operand):

        # Empty number for the result
        result = Number(0.0)
        result.truncated = self.truncated or operand.truncated

        overflow = False

        # Long-multiply
        for selfExp in EXPONENTS:
            for operandExp in EXPONENTS:

                resMantissa = self.column[selfExp].mantissa * operand.column[operandExp].mantissa

                if resMantissa==0.0:
                    continue
                # if

                resExponent = self.column[selfExp].exp + operand.column[operandExp].exp

                # Detect overflow
                if resExponent not in result.column:
                    if(_truncPrintEnabled): print("(Multiplication truncated because exponent [%d] is outside supported range)" % resExponent)
                    result.truncated = True
                    overflow = True
                    break
                # if

                result.column[resExponent].mantissa += resMantissa
            # for

            if overflow:
                break
            # if
        # for

        result.Clean()

        if _arithPrintEnabled: print("%s * %s = %s" % (self.Text(), operand.Text(), result.Text()))

        return result
    # def

    def __truediv__(self, operand):

        # Suppress prints for div sub-arithmetic
        global _arithPrintEnabled
        arithPrintEnabled = _arithPrintEnabled
        _arithPrintEnabled = False

        operand = operand.Clone().Clean()

        # Create remainder from current value
        remainder = self.Clone().Clean()

        # Create an empty number for the result
        quotient = Number(0.0)

        # Propagate incoming truncation state
        quotient.truncated = self.truncated or operand.truncated
        remainder.truncated = self.truncated

        # Find leading exponent
        divLeadExp = operand.LeadingExp()
        if divLeadExp is None:
            # Construct 1/inf for true-zero operand
            effective_divisor = Number(0.0, 0.0, 1.0)
            effective_divisor.Clean()
            effective_divisor.truncated = operand.truncated

            divLeadExp = effective_divisor.LeadingExp()
            divLeadCoeff = effective_divisor.column[divLeadExp].mantissa
        else:
            effective_divisor = operand
            divLeadCoeff = operand.column[divLeadExp].mantissa
        # if

        # Iterate to a long-division solution
        max_steps = 100
        hit_step_limit = True
        for step in range(max_steps):
            remainder.Clean()

            if remainder.IsTrueZero():
                hit_step_limit = False
                break
            # if

            remLeadExp = remainder.LeadingExp()
            remLeadCoeff = remainder.column[remLeadExp].mantissa

            qExp = remLeadExp - divLeadExp
            qCoeff = remLeadCoeff / divLeadCoeff

            # Check for overflow
            if qExp not in quotient.column:
                if(_truncPrintEnabled): print("Division truncated because next quotient term [%d] is outside supported range." % (qExp))
                quotient.truncated = True
                hit_step_limit = False
                break
            # if

            qTerm = Number(0.0)
            qTerm.column[qExp].mantissa = qCoeff
            qTerm.Clean()

            quotient = quotient + qTerm
            mult_result = qTerm * effective_divisor
            remainder = remainder - mult_result

            # Propagate truncation from internal operations
            if qTerm.truncated or mult_result.truncated or remainder.truncated:
                quotient.truncated = True
            # if

        # for

        if hit_step_limit and not remainder.IsTrueZero():
            if _truncPrintEnabled: print("Warning: division truncated after %d steps (max_steps reached)" % max_steps)
            quotient.truncated = True
        # if

        quotient.Clean()

        # Restore arithmetic printing
        _arithPrintEnabled = arithPrintEnabled

        if remainder.IsTrueZero():
            if _arithPrintEnabled: print("%s / %s = %s" % (self.Text(), operand.Text(), quotient.Text()))
        else:
            if _arithPrintEnabled: print("%s / %s = %s rem=%s" % (self.Text(), operand.Text(), quotient.Text(), remainder.Text()))
        # if
        return quotient
    # def

    def __eq__(self, operand):

        self.Clean()
        operand.Clean()

        for i in EXPONENTS:
            if self.column[i].mantissa != operand.column[i].mantissa:
                return False
            # if
        # for

        # Made it through all disproofs
        return True
    # def
# class

class Matrix:

    def __init__(self, name, matrix):
        self.name = name
        self.matrix = matrix
    # def

    def ForwardSubstitute(self, L, b):
        n = len(L)
        y = [Number(0.0) for _ in range(n)]

        for i in range(n):
            sum_ = Number(0.0)
            for j in range(i):
                sum_ += L[i][j] * y[j]
            # for

            # L[i][i] should be 1, but allow general division just in case
            y[i] = (b[i] - sum_) / L[i][i]
        # for

        return y
    # def

    def BackwardSubstitute(self, U, y):
        n = len(U)
        x = [Number(0.0) for _ in range(n)]

        for i in reversed(range(n)):
            sum_ = Number(0.0)
            for j in range(i + 1, n):
                sum_ += U[i][j] * x[j]
            # for

            # In your system, division by zero is allowed, so do not block it.
            x[i] = (y[i] - sum_) / U[i][i]
        # for

        return x
    # def

    def ApplyPermutation(self, P, vec):
        return [vec[P[i]].Clone() for i in range(len(P))]
    # def

    def InvertFromLu(self, L, U, P):
        n = len(L)
        inverse_cols = []

        for i in range(n):
            # Solve A x = e_i
            e = [Number(0.0) for _ in range(n)]
            e[i] = Number(1.0)

            # Since P*A = L*U, solve L*U*x = P*e
            pe = self.ApplyPermutation(P, e)

            y = self.ForwardSubstitute(L, pe)
            x = self.BackwardSubstitute(U, y)
            inverse_cols.append(x)
        # for

        # Transpose columns -> rows
        return [list(col) for col in zip(*inverse_cols)]
    # def

    def LuDecompose(self):
        n = len(self.matrix)

        # Working copy of A
        A = [[self.matrix[i][j].Clone() for j in range(n)] for i in range(n)]

        L = [[Number(0.0) for _ in range(n)] for _ in range(n)]
        U = [[Number(0.0) for _ in range(n)] for _ in range(n)]
        P = list(range(n))

        for i in range(n):

            # Find a row with nonzero entry in column i, at or below row i.
            pivot = i
            while pivot < n and A[pivot][i] == Number(0.0):
                pivot += 1
            # while

            # If no nonzero pivot exists, keep going.
            # In your arithmetic system, later divisions may still produce a result.
            if pivot == n:
                if _badMatrixPrintEnabled:
                    print("Warning! Column %d has no nonzero pivot; continuing without row swap." % i)
                # if
                pivot = i
            # if

            # Swap rows in A, permutation P, and the already-built part of L
            if pivot != i:
                A[i], A[pivot] = A[pivot], A[i]
                P[i], P[pivot] = P[pivot], P[i]

                for j in range(i):
                    L[i][j], L[pivot][j] = L[pivot][j], L[i][j]
                # for
            # if

            # Build U row i
            for k in range(i, n):
                sum_ = Number(0.0)
                for j in range(i):
                    sum_ += L[i][j] * U[j][k]
                # for
                U[i][k] = self.matrix[0][0]  # temporary placeholder
                U[i][k] = A[i][k] - sum_
            # for

            # Unit diagonal in L
            L[i][i] = Number(1.0)

            # Build L column i below diagonal
            for k in range(i + 1, n):
                sum_ = Number(0.0)
                for j in range(i):
                    sum_ += L[k][j] * U[j][i]
                # for

                # Keep divide-by-zero semantics from Number.__truediv__
                L[k][i] = (A[k][i] - sum_) / U[i][i]
            # for
        # for

        return L, U, P
    # def

    def Invert(self):
        L, U, P = self.LuDecompose()
        inv = self.InvertFromLu(L, U, P)

        for row in inv:
            for value in row:
                value.Round()
            # for
        # for

        return Matrix(self.name + "-Inv", inv)
    # def

    def Display(self):
        print("Name:%s" % (self.name))
        for row in self.matrix:
            for col in row:
                print("  " + col.Text() + ",", end="")
            # for
            print()
        # for
        print()
    # def

    def DisplayReal(self):
        print("Name:%s (real)" % (self.name))
        for row in self.matrix:
            for col in row:
                print(" %.3f," % (col.Real()), end="")
            # for
            print()
        # for
        print()
    # def

# class

# ---- End BaseInfinity numeric system ----



class CircuitMatrixTool:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Circuit Matrix Tool (Resistors + Voltage Sources)")
        self.root.geometry("1350x860")

        self.nodes = []
        self.resistors = []
        self.vsources = []
        self.diagnostics = []

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

        ttk.Label(
            frm,
            text="Nodes are loaded from the JSON file.",
            justify="left",
        ).pack(anchor="w")

        self.nodes_list = tk.Listbox(frm, height=8, width=48)
        self.nodes_list.pack(fill="x", pady=(8, 0))

    def _build_component_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Components", padding=8)
        frm.pack(fill="x", pady=(0, 8))

        ttk.Label(
            frm,
            text="Resistors and voltage sources are loaded from the JSON file.",
            justify="left",
        ).pack(anchor="w")

        self.components_list = tk.Listbox(frm, height=12, width=48)
        self.components_list.pack(fill="x", pady=(8, 0))

    def _build_actions_panel(self, parent):
        frm = ttk.LabelFrame(parent, text="Actions", padding=8)
        frm.pack(fill="x")

        ttk.Button(frm, text="Generate Matrix", command=self.generate_matrix).pack(fill="x", pady=2)
        ttk.Button(frm, text="Auto Layout Nodes", command=self.auto_layout_nodes).pack(fill="x", pady=2)
        ttk.Button(frm, text="Load JSON", command=self.load_json).pack(fill="x", pady=2)
        ttk.Button(frm, text="Save JSON", command=self.save_json).pack(fill="x", pady=2)

        note = (
            "Circuit editing has been removed from the GUI.\n"
            "Edit the JSON file directly, then reload it here.\n\n"
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
        self.refresh_all()
        self.generate_matrix()

    def refresh_all(self):
        self.refresh_lists()
        self.redraw_canvas()

    def refresh_lists(self):
        self.nodes_list.delete(0, "end")
        for node in self.nodes:
            self.nodes_list.insert("end", f'{node["name"]}: ({int(node["x"])}, {int(node["y"])})')

        self.components_list.delete(0, "end")
        for r in self.resistors:
            value_text = "inf" if isinstance(r["value"], float) and math.isinf(r["value"]) else r["value"]
            if self.is_zero_ohm(r["value"]):
                item_text = f'BASE-INF: {r["name"]}: {r["n1"]} -- {r["n2"]}   {value_text} Ohm (1/0 -> UnitInfinity)'
                self.components_list.insert("end", item_text)
                self.components_list.itemconfig("end", foreground="red")
            else:
                self.components_list.insert("end", f'{r["name"]}: {r["n1"]} -- {r["n2"]}   {value_text} Ohm')
        for v in self.vsources:
            self.components_list.insert("end", f'{v["name"]}: {v["p"]} (+) , {v["n"]} (-)   {v["value"]} V')

    def find_node(self, name: str):
        for node in self.nodes:
            if node["name"] == name:
                return node
        return None

    @staticmethod
    def is_zero_ohm(value) -> bool:
        try:
            return (not (isinstance(value, float) and math.isinf(value))) and abs(float(value)) < 1e-15
        except Exception:
            return False

    def add_diagnostic(self, severity: str, message: str):
        self.diagnostics.append({"severity": severity, "message": message})

    def show_diagnostics(self):
        self.results_text.delete("1.0", "end")

        if not self.diagnostics:
            self._append("No diagnostics.\n")
            return

        self._append("Diagnostics:\n")
        for item in self.diagnostics:
            self._append(f"  {item['severity']}: {item['message']}\n")

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
            messagebox.showerror("Save failed", f"Could not save JSON file:\n{exc}")
            return

        messagebox.showinfo("Saved", f"Circuit saved to:\n{path}")

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
            messagebox.showerror("Load failed", f"Could not load JSON file:\n{exc}")

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
            resistance_text = "inf" if isinstance(resistor["value"], float) and math.isinf(resistor["value"]) else f'{resistor["value"]}'
            self._draw_component_line(
                resistor["n1"],
                resistor["n2"],
                resistor["name"],
                f"{resistance_text} Ω",
                "#1f77b4"
            )

        for source in self.vsources:
            self._draw_component_line(
                source["p"],
                source["n"],
                source["name"],
                f'{source["value"]} V',
                "#d62728",
                polarity=True
            )

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
        self.diagnostics = []

        try:
            result = self.build_mna_system()
        except ValueError as exc:
            if not self.diagnostics:
                self.add_diagnostic("ERROR", str(exc))
            self.show_diagnostics()
            messagebox.showerror("Cannot generate matrix", str(exc))
            return
        except ZeroDivisionError as exc:
            self.add_diagnostic("ERROR", f"Divide by zero intercepted: {exc}")
            self.show_diagnostics()
            messagebox.showerror("Divide by zero intercepted", str(exc))
            return
        except Exception as exc:
            self.add_diagnostic("ERROR", f"Unexpected error: {exc}")
            self.show_diagnostics()
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

        G = [[Number(0.0) for _ in range(m)] for _ in range(m)]
        B = [[Number(0.0) for _ in range(k)] for _ in range(m)]
        I = [Number(0.0) for _ in range(m)]
        E = [Number(0.0) for _ in range(k)]

        def stamp_conductance(n1, n2, g):
            if n1 != "GND":
                i = node_index[n1]
                G[i][i] = G[i][i] + g
            if n2 != "GND":
                j = node_index[n2]
                G[j][j] = G[j][j] + g
            if n1 != "GND" and n2 != "GND":
                i = node_index[n1]
                j = node_index[n2]
                G[i][j] = G[i][j] - g
                G[j][i] = G[j][i] - g

        for resistor in self.resistors:
            val = resistor["value"]

            if isinstance(val, float) and math.isinf(val):
                continue

            if self.is_zero_ohm(val):
                self.add_diagnostic(
                    "INFO",
                    f"BaseInfinity handled 1/0 while stamping conductance for resistor "
                    f"'{resistor['name']}' between {resistor['n1']} and {resistor['n2']}: "
                    f"0 Ohm resistance gives UnitInfinity conductance."
                )

            g = Number(1.0) / Number(val)
            stamp_conductance(resistor["n1"], resistor["n2"], g)

        for col, source in enumerate(self.vsources):
            p = source["p"]
            n = source["n"]
            if p != "GND":
                B[node_index[p]][col] = B[node_index[p]][col] + Number(1.0)
            if n != "GND":
                B[node_index[n]][col] = B[node_index[n]][col] - Number(1.0)
            E[col] = Number(source["value"])

        size = m + k
        A = [[Number(0.0) for _ in range(size)] for _ in range(size)]
        z = [Number(0.0) for _ in range(size)]

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

        node_voltages = {"GND": Number(0.0)}
        for i, name in enumerate(node_names):
            node_voltages[name] = solution[i]

        resistor_flows = []
        for resistor in self.resistors:
            n1 = resistor["n1"]
            n2 = resistor["n2"]
            val = resistor["value"]
            vdrop = node_voltages[n1] - node_voltages[n2]

            if isinstance(val, float) and math.isinf(val):
                current = Number(0.0)
            else:
                if self.is_zero_ohm(val):
                    self.add_diagnostic(
                        "INFO",
                        f"BaseInfinity handled Vdrop/0 while calculating current for resistor "
                        f"'{resistor['name']}' between {n1} and {n2}."
                    )
                current = vdrop / Number(val)

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
        """
        Solve A*x=b using the BaseInfinity Matrix inverse. This keeps divide-by-zero
        semantics inside Number.__truediv__ instead of raising float ZeroDivisionError.
        """
        n = len(A)
        if n == 0:
            return []

        inv = Matrix("MNA", A).Invert().matrix
        x = []
        for r in range(n):
            total = Number(0.0)
            for c in range(n):
                total = total + (inv[r][c] * b[c])
            total.Round()
            x.append(total)
        return x

    def show_result(self, result):
        self.results_text.delete("1.0", "end")

        node_names = result["node_names"]
        vsource_names = result["vsource_names"]

        unknowns = [f"V({name})" for name in node_names] + [f"I({name})" for name in vsource_names]

        if self.diagnostics:
            self._append("Diagnostics:\n")
            for item in self.diagnostics:
                self._append(f"  {item['severity']}: {item['message']}\n")
            self._append("\n")

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

        self._append("Named results:\n")
        for name, value in zip(unknowns, result["x"]):
            unit = "V" if name.startswith("V(") else "A"
            self._append(f"  {name} = {self.format_value(value)} {unit}  (real={self.format_real(value)})\n")

        self._append("\nResistor flows (positive from Node A to Node B):\n")
        for flow in result["resistor_flows"]:
            resistance = flow["resistance"]
            if isinstance(resistance, float) and math.isinf(resistance):
                resistance_text = "inf"
            else:
                resistance_text = f"{resistance:.6g}"

            self._append(
                f"  {flow['name']}: I = {self.format_value(flow['current'])} A, "
                f"Vdrop = {self.format_value(flow['voltage_drop'])} V, "
                f"R = {resistance_text} Ohm, "
                f"direction {flow['from_node']} -> {flow['to_node']}\n"
            )

    def _append(self, text: str):
        self.results_text.insert("end", text)

    @staticmethod
    def format_value(value):
        if isinstance(value, Number):
            return value.Text()
        return f"{value:.6g}"

    @staticmethod
    def format_real(value):
        if isinstance(value, Number):
            real = value.Real()
            if isinstance(real, float) and math.isinf(real):
                return "Inf"
            return f"{real:.6g}"
        return f"{value:.6g}"

    @staticmethod
    def format_matrix(M):
        if not M:
            return "[ ]"
        lines = []
        for row in M:
            lines.append("[ " + "  ".join(f"{CircuitMatrixTool.format_value(val):>18}" for val in row) + " ]")
        return "\n".join(lines)

    @staticmethod
    def format_vector(v):
        return "[ " + "  ".join(f"{CircuitMatrixTool.format_value(val):>18}" for val in v) + " ]^T"


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