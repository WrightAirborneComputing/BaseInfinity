import math

EPS = 1e-9
EXPONENTS = [8, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8]

def IsZero(value):
    return math.fabs(value) < EPS
# def

class Column:

    def __init__(self, infPower, mantissa):
        self.mantissa = float(mantissa)
        self.exp = int(infPower)
    # def

    def Text(self):
        return "%f" % self.mantissa
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

        # Instrumentation
        self.print_enabled = True
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
        result.print_enabled = self.print_enabled
        return result
    # def

    def Clean(self):
        for e in EXPONENTS:
            if IsZero(self.column[e].mantissa):
                self.column[e].mantissa = 0.0
            # if
        # for

        return self
    # def

    def Round(self):
        # Force the last (rightmost) negative exponent column to zero
        #last_neg_exp = min(EXPONENTS)  # = -7
        #self.column[last_neg_exp].mantissa = 0.0

        return self
    # def

    def WarnAndTruncate(self, exp, mantissa, context):
        if not IsZero(mantissa):
            print("Warning: %s produced exponent %d outside supported range; truncating term %g*n^%d" %
                  (context, exp, mantissa, exp))
            # Truncate
        # if
    # def

    def AddToExponent(self, exp, mantissa, context):
        if exp in self.column:
            self.column[exp].mantissa += mantissa
        else:
            self.WarnAndTruncate(exp, mantissa, context)
            self.truncated = True
        # if
    # def

    def IsTrueZero(self):
        for e in EXPONENTS:
            if not IsZero(self.column[e].mantissa):
                return False
            # if
        # for
        return True
    # def

    def IsUnitZero(self):
        self.Clean()

        for e in EXPONENTS:
            if e == -1:
                if not IsZero(self.column[e].mantissa - 1.0):
                    return False
                # if
            else:
                if not IsZero(self.column[e].mantissa):
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
                if not IsZero(self.column[e].mantissa - 1.0):
                    return False
                # if
            else:
                if not IsZero(self.column[e].mantissa):
                    return False
                # if
            # if
        # for

        return True
    # def

    def LeadingExp(self):
        for e in EXPONENTS:
            if not IsZero(self.column[e].mantissa):
                return e
            # if
        # for
        return None
    # def

    def TrailingExp(self):
        for e in reversed(EXPONENTS):
            if not IsZero(self.column[e].mantissa):
                return e
            # if
        # for
        return None
    # def

    def EnablePrint(self):
        self.print_enabled = True
    # def

    def DisablePrint(self):
        self.print_enabled = False
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
        used = [exp for exp in EXPONENTS if not IsZero(self.column[exp].mantissa)]

        # Determine symmetric range around 0
        k = max(abs(min(used)), abs(max(used)))

        # Build symmetric list (only within supported EXPONENTS)
        values = []
        for exp in EXPONENTS:
            if abs(exp) <= k:
                values.append("%.3f" % self.column[exp].mantissa)
            # if
        # for

        return "[" + ",".join(values) + "]"
    # def

    def Real(self):
        lead = self.LeadingExp()
        if lead is None:
            return self.column[0].mantissa
        elif lead > 0:
            return float('inf')
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
        if self.print_enabled:
            print("%s + %s = %s" % (self.Text(), operand.Text(), result.Text()))
        return result
    # def

    def __sub__(self, operand):
        result = Number(0.0)
        result.truncated = self.truncated or operand.truncated
        for i in EXPONENTS:
            result.column[i].mantissa = self.column[i].mantissa - operand.column[i].mantissa
        # for
        result.Clean()
        if self.print_enabled:
            print("%s - %s = %s" % (self.Text(), operand.Text(), result.Text()))
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

                if IsZero(resMantissa):
                    continue
                # if

                resExponent = self.column[selfExp].exp + operand.column[operandExp].exp

                # Detect overflow
                if resExponent not in result.column:
                    result.WarnAndTruncate(resExponent, resMantissa, "__mul__")
                    print("Multiplication truncated because exponent [%d] is outside supported range." % resExponent)
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
        result.Round()

        if self.print_enabled:
            print("%s * %s = %s" % (self.Text(), operand.Text(), result.Text()))
        # if

        return result
    # def

    def __truediv__(self, operand):

        operand = operand.Clone().Clean()

        # Create remainder with current value
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
                quotient.WarnAndTruncate(qExp, qCoeff, "__truediv__")
                print("Division truncated because next quotient term [%d] is outside supported range." % (qExp))
                quotient.truncated = True
                hit_step_limit = False
                break
            # if

            qTerm = Number(0.0)
            qTerm.column[qExp].mantissa = qCoeff
            qTerm.Clean()

            # Handle inst
            quotient.DisablePrint()
            qTerm.DisablePrint()
            remainder.DisablePrint()
            effective_divisor.DisablePrint()

            quotient = quotient + qTerm
            mult_result = qTerm * effective_divisor
            remainder = remainder - mult_result

            # Propagate truncation from internal operations
            if qTerm.truncated or mult_result.truncated or remainder.truncated:
                quotient.truncated = True
            # if

            # Handle inst
            quotient.EnablePrint()
            qTerm.EnablePrint()
            remainder.EnablePrint()
            effective_divisor.EnablePrint()

        # for

        if hit_step_limit and not remainder.IsTrueZero():
            print("Warning: division truncated after %d steps (max_steps reached)" % max_steps)
            quotient.truncated = True
        # if

        quotient.Clean()
        quotient.Round()

        if not self.print_enabled:
            pass
        elif remainder.IsTrueZero():
            print("%s / %s = %s" % (self.Text(), operand.Text(), quotient.Text()))
        else:
            print("%s / %s = %s+%s" % (self.Text(), operand.Text(), quotient.Text(), remainder.Text()))
        # if
        return quotient
    # def

    def __eq__(self, operand):

        self.Clean()
        operand.Clean()

        for i in EXPONENTS:
            if not IsZero(self.column[i].mantissa - operand.column[i].mantissa):
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
            y[i] = b[i] - sum_
        # for
        return y
    # def

    def BackwardSubstitute(self, U, y):
        n = len(U)
        x = [Number(0.0) for _ in range(n)]
        for i in reversed(range(n)):
            if U[i][i] == Number(0):
                print("Warning! Zero diagonal element in U during back substitution.")
            # if
            sum_ = Number(0.0)
            for j in range(i + 1, n):
                sum_ += U[i][j] * x[j]
            # for
            x[i] = (y[i] - sum_) / U[i][i]
        # for
        return x
    # def

    def InvertFromLu(self, L, U):
        n = len(L)
        inverse = []
        for i in range(n):
            # Solve A x = e_i
            e = [Number(0.0) for _ in range(n)]
            e[i] = Number(1.0)
            y = self.ForwardSubstitute(L, e)
            x = self.BackwardSubstitute(U, y)
            inverse.append(x)
        # for

        # Columns are in rows; transpose the matrix
        return [list(col) for col in zip(*inverse)]
    # def

    def LuDecompose(self):
        n = len(self.matrix)
        L = [[Number(0.0) for _ in range(n)] for _ in range(n)]
        U = [[Number(0.0) for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for k in range(i, n):
                sum_ = Number(0.0)
                for j in range(i):
                    sum_ += L[i][j] * U[j][k]
                # for
                U[i][k] = self.matrix[i][k] - sum_
            # for

            for k in range(i, n):
                if i == k:
                    L[i][i] = Number(1.0)
                else:
                    sum_ = Number(0.0)
                    for j in range(i):
                        sum_ += L[k][j] * U[j][i]
                    # for
                    if U[i][i] == Number(0.0):
                        print("Warning! Zero pivot encountered. LU decomposition fails.")
                    # if
                    L[k][i] = (self.matrix[k][i] - sum_) / U[i][i]
                # if
            # for
        # for

        return L, U
    # def

    def Invert(self):
        L, U = self.LuDecompose()
        inv = self.InvertFromLu(L, U)
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

def RunArithTests():
    real1        = Number(1.0)             # 1
    real2        = Number(2.0)             # 2
    trueZero     = Number(0.0)             # 0
    unitZero     = Number(0.0, 0.0, 1.0)   # n^-1
    unitInfinity = Number(1.0, 0.0, 0.0)   # n^1
    infPlusOne   = Number(1.0, 1.0, 0.0)   # 1 + n^1
    strange1     = Number(1.23, 4.56, 7.89)
    strange2     = Number(9.87, 6.54, 3.21)

    # Add two reals
    result = real1 + real2

    # Sub two reals
    result = real1 - real2

    # Mult two reals
    result = real2 * real2

    # Div two reals
    result = real1 / real2

    # Mult one by unit infinity
    result = real1 * unitInfinity

    # Div reals by unit infinity
    result = real1 / unitInfinity
    result = real2 / unitInfinity

    # Div real by zero
    result = real1 / trueZero

    # Mult two by unit infinity
    result = real2 * unitInfinity

    # Mult unit infinity by 1
    result = unitInfinity * real1

    # Div unit infinity by 1
    result = unitInfinity / real1

    # Mult unit zero by unit infinity
    result = unitZero * unitInfinity

    # Div two by unit infinity
    result = real2 / unitInfinity

    # Mult back out to recover the two
    result = result * unitInfinity

    # Multiply real-plus-infinity and real
    result = infPlusOne * real2

    # Divide back out
    result = result / real2

    # Divide by a real-plus-infinity (itself)
    result = infPlusOne / infPlusOne

    # Divide by a real-plus-infinity (2 x itself)
    result = infPlusOne / (infPlusOne * real2)

    # Add strange numbers to see if subtract reverses it OK
    result = strange1 + strange2
    result = result - strange2

    # Multiply strange numbers to see if divide reverses it OK
    result = strange1 * strange2
    result = result / strange2

    # Divide strange numbers to see if multiply reverses it OK
    result = strange1 / strange2
    result = result * strange2

    # Values that crop up in matrix manipulation
    #val1 = Number(-0.500, 0.000, 0.000)
    #val2 = Number( 1.000, 0.500, 0.000)
    #result = val1 / val2
    #result = result * val2
# def

def RunMatrixTest(mat):

    mat_inv = mat.Invert()
    mat_inv_inv = mat_inv.Invert()
    mat.Display()
    mat_inv.Display()
    mat_inv_inv.Display()
    mat_inv_inv.DisplayReal()

#def

def RunMatrixTests():

    # Matrix manipulation
    A = Matrix("A",
               [
                   [Number(4), Number(7)],
                   [Number(2), Number(6)]
               ])
    # Correct answer is:
    # [0.600]
    # [-0.700]
    # [-0.200]
    # [0.400]
    RunMatrixTest(A)

    singular = Matrix("Singular",
                      [
                          [Number(2), Number(4)],
                          [Number(1), Number(2)]
                      ])
    RunMatrixTest(singular)

    infinityZero = Matrix("InfinityZero",
                      [
                          [Number(0), Number(1,0,0)],
                          [Number(0), Number(0)]
                      ])
    RunMatrixTest(infinityZero)

    infinityTen = Matrix("InfinityTen",
                      [
                          [Number(10), Number(1,0,0)],
                          [Number(10), Number(0)]
                      ])
    RunMatrixTest(infinityTen)

# def

RunArithTests()
RunMatrixTests()
