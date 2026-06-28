import math

from BaseInfinityLib import (
    Number,
    SetArithmeticPrintEnabled,
    SetTruncationPrintEnabled,
    SetBadMatrixPrintEnabled,
)
from MatrixLib import Matrix

# Instrumentation defaults
SetArithmeticPrintEnabled(False)
SetTruncationPrintEnabled(True)
SetBadMatrixPrintEnabled(True)

def RunArithTests():

    SetArithmeticPrintEnabled(True)

    real1        = Number(1.0)             # 1
    real2        = Number(2.0)             # 2
    trueZero     = Number(0.0)             # 0
    minusOne     = Number(-1.0)            # -1
    unitZero     = Number(0.0, 0.0, 1.0)   # n^-1
    unitInfinity = Number(1.0, 0.0, 0.0)   # n^1
    infPlusOne   = Number(1.0, 1.0, 0.0)   # 1 + n^1
    strange1     = Number(1.23, 4.56, 7.89)
    strange2     = Number(9.87, 6.54, 3.21)

    # Add two reals
    print("\nAdd two reals")
    result = real1 + real2

    # Sub two reals
    print("\nSub two reals")
    result = real1 - real2

    # Mult two reals
    print("\nMult two reals")
    result = real2 * real2

    # Div two reals
    print("\nDiv two reals")
    result = real1 / real2

    # Mult one by unit infinity
    print("\nMult one by unit infinity")
    result = real1 * unitInfinity

    # Div reals by unit infinity
    print("\nDiv reals by unit infinity")
    result = real1 / unitInfinity
    result = real2 / unitInfinity

    # Multiply zero by -1
    print("\nMultiply zero by -1")
    result = trueZero * minusOne

    # Div real by zero
    print("\nDiv real by zero")
    result = real1 / trueZero

    # Divide zero by zero
    print("\nDivide zero by zero")
    result = trueZero / trueZero

    # Mult two by unit infinity
    print("\nMult two by unit infinity")
    result = real2 * unitInfinity

    # Mult unit infinity by 1
    print("\nMult unit infinity by 1")
    result = unitInfinity * real1

    # Div unit infinity by 1
    print("\nDiv unit infinity by 1")
    result = unitInfinity / real1

    # Mult unit zero by unit infinity
    print("\nMult unit zero by unit infinity")
    result = unitZero * unitInfinity

    # Div two by unit infinity to see if mult recovers it OK
    print("\nDiv two by unit infinity to see if mult recovers it OK")
    result = real2 / unitInfinity
    result = result * unitInfinity

    # Multiply real-plus-infinity and real to see if divide reverses it OK
    print("\nMultiply real-plus-infinity and real to see if divide reverses it OK")
    result = infPlusOne * real2
    result = result / real2

    # Divide by a real-plus-infinity (itself)
    print("\nDivide by a real-plus-infinity (itself)")
    result = infPlusOne / infPlusOne

    # Divide by a real-plus-infinity (2 x itself)
    print("\nDivide by a real-plus-infinity (2 x itself)")
    result = infPlusOne / (infPlusOne * real2)

    # Add strange numbers to see if subtract reverses it OK
    print("\nAdd strange numbers to see if subtract reverses it OK")
    result = strange1 + strange2
    result = result - strange2

    # Multiply strange numbers to see if divide reverses it OK
    print("\nMultiply strange numbers to see if divide reverses it OK")
    result = strange1 * strange2
    result = result / strange2

    # Divide strange numbers to see if multiply reverses it OK
    print("\nDivide strange numbers to see if multiply reverses it OK")
    result = strange1 / strange2
    result = result * strange2

    # Values that crop up in matrix manipulation
    #val1 = Number(-0.500, 0.000, 0.000)
    #val2 = Number( 1.000, 0.500, 0.000)
    #result = val1 / val2
    #result = result * val2
# def

def RunMatrixTest(mat):
    SetArithmeticPrintEnabled(False)

    print("\nTesting matrix [%s]" % (mat.name))
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

    singular1 = Matrix("Singular1",
                      [
                          [Number(2), Number(4)],
                          [Number(1), Number(2)]
                      ])
    RunMatrixTest(singular1)

    singular2 = Matrix("Singular2",
                      [
                          [Number(3), Number(6)],
                          [Number(5), Number(10)]
                      ])
    RunMatrixTest(singular2)

    infinityZeroes = Matrix("InfinityZeroes",
                      [
                          [Number(0), Number(1,0,0)],
                          [Number(0), Number(0)]
                      ])
    RunMatrixTest(infinityZeroes)

    infinityTrueZero = Matrix("InfinityTrueZero",
                      [
                          [Number(10), Number(1,0,0)],
                          [Number(7),  Number(0)]
                      ])
    RunMatrixTest(infinityTrueZero)

    infinityUnitZero = Matrix("InfinityUnitZero",
                      [
                          [Number(10), Number(1,0,0)],
                          [Number(7),  Number(0,0,1)]
                      ])
    RunMatrixTest(infinityUnitZero)

# def

RunArithTests()
RunMatrixTests()
