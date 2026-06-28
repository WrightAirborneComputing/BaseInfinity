from BaseInfinityLib import Number, GetBadMatrixPrintEnabled


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
                if GetBadMatrixPrintEnabled():
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

