
  #include <stdio.h> 
  #include "cpuidh.h"
  #include <stdlib.h> 
  #include <unistd.h>   
  #include <math.h>

int main()
{
    int i, j;
    double startTime;
    double runSecs = 0;
    double data[1250000];

    for (i=0; i<1250000; i++)
    {
       data[i] = (double)i;
    }

    local_time();
    printf("\n  %s", timeday);

    getSecs();
    startTime = theseSecs;
    double  x = 0.5;
    double  y = 0.5;
    double t2 = 2.0;
    double t  =  0.49999975;
    char   input[10];

    for (i=0; i<10000; i++)
    {
       for (j=0; j<333; j++)
       {
            x = t*atan(t2*sin(x)*cos(x)/(cos(x+y)+cos(x-y)-1.0));
            y = t*atan(t2*sin(y)*cos(y)/(cos(x+y)+cos(x-y)-1.0));
       }
    }
    getSecs();
    runSecs = theseSecs - startTime;

    printf("\n  Time %20.10f secs %12.4f\n", runSecs, y);    
 
    local_time();
    printf("\n  %s\n", timeday);
    
    getDetails();
    printf("\n");
    for (i=1; i<10; i++)
    {
        printf("%s\n", configdata[i]);
    }
    printf("\n ");
    if (hasMMX)   printf(" hasMMX");
    if (hasSSE)   printf(" hasSSE");
    if (hasSSE2)  printf(" hasSSE2");
    if (hasSSE3)  printf(" hasSSE3");
    if (has3DNow) printf(" has3DNow");
    printf("\n\n");
    printf("  Press Enter\n");
    int g  = getchar();  
 
    return 0;
}




