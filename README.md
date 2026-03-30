Let’s use a base-infinity number system, and why that would be useful

I’ve always had a problem div-by-zero in CompSci. Like every software engineer, a little piece of me dies inside when a div-by-zero exception goes off during testing: I hang some God-awful code around it and hope that there isn’t another ticking bomb out there in the solution-space.

Take two calculations:
1/inf==0 & 2/inf==0
There has been information loss, effectively a floating-point truncation error. So, if we add 1/inf and 2/inf, we get zero. Even if we multiply back out by infinity, we still get zero.
But (1/inf + 2/inf)*inf => (1+2) / (inf/inf), so if we multiply by infinity it “should” get our original 1+2 = 3 back. It would be nice to avoid that data-loss.
“Surely there are no practical use cases where we multiply back out by inf, so surely this is all a bit academic?” you say. However, yes we do so no it isn’t. More on that later.
I was helping Jamie with his homework the other week, keeping square-root of 2 and 3 in “surd form” in algebra, to avoid creating a truncation error. We were kicking this around over bacon sandwiches at the weekend, and I thought that we can create a number system that accommodates “different zeros”, where they are constructed as multiples of 1/inf (i.e. inf ^ -1), thus preserving the underlying information.
We can then do arithmetic with a basic number system consisting of real numbers and 1/inf, but it introduces a problem when we start adding infinites and we need to account for the multiple infinities stacking up. It gets worse when multiplying, because we need to account for higher powers of inf.
I think that we can handle this by putting everything into a kind of meta-number-system of Base Infinity.
 
Our entire real-number universe is then just one column in the powers-of-inf table (yellow in the above), where inf^0==1. The decimal point (or binary point etc, depending on your real-number base du jour) sits below the units line in that column.
Everything left of the inf^0 column is where an infinite number of infinities live: everything right of it is the infinite space where all the different kinds of zero are found.
I’m sure a different one has been done years ago, but I’m going to introduce a notation system:
[inf^n,inf^(n-1),…,inf^2,inf^1,inf^0.inf^-1,inf^-2,…] (Note the “infinital point” between inf^0 and inf^-1)
Thus 1 => [0,1.0,0] or [1.0]
“True zero” => [0.0]
1/inf zero => [0.1]
“The one true infinity” (Jamie and Steve terminology) => [1,0.0]
 
Needless to say, I need to code this into a class library (done!), but you can already see that the real-number part where 6 * 12 = 72 drops out nicely, even though the number would appear to be infinity using conventional methods.
It has interesting implications for the old “Is 0.99999 recuring equal to 1?” debate (lookin’ at you Sarah Nash https://www.linkedin.com/in/sarah-nash-ceng-7a5781a9/?originalSubdomain=uk ). There’s a “proof” that goes 1/9=0.11111., so (1/9 * 9) = (0.11111. * 9), so they are the same right? Using my base-inf though, I can claim that 1 is [0,1.0,0] – [0,0.0], but 0.99999. is [0,1.0,0] – [0,0.1], so they’re different because they are differentiated in the “zero-space”. Let the lynchings begin.
So what’s the use of this? Surely we never have a practical use case where we need to multiply back out by inf? Yes we do: when we divide-by-zero.
