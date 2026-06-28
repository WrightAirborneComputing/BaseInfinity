import math

MAX_EXPONENT = 5
EXPONENTS = list(range(MAX_EXPONENT, -MAX_EXPONENT - 1, -1))

# Instrumentation flags for this module and MatrixLib.
# Keep them here so all users of Number see the same settings.
_arithPrintEnabled = False
_truncPrintEnabled = True
_badMatrixPrintEnabled = True

def IsZero(value):
    return math.fabs(value) < 1e-12
# def

def SetArithmeticPrintEnabled(enabled):
    global _arithPrintEnabled
    _arithPrintEnabled = bool(enabled)
# def

def GetArithmeticPrintEnabled():
    return _arithPrintEnabled
# def

def SetTruncationPrintEnabled(enabled):
    global _truncPrintEnabled
    _truncPrintEnabled = bool(enabled)
# def

def GetTruncationPrintEnabled():
    return _truncPrintEnabled
# def

def SetBadMatrixPrintEnabled(enabled):
    global _badMatrixPrintEnabled
    _badMatrixPrintEnabled = bool(enabled)
# def

def GetBadMatrixPrintEnabled():
    return _badMatrixPrintEnabled
# def

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

