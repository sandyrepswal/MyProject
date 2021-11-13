class SortingAlgos:

    def bubbleSort(self,inpArr):
        for i in range(0,len(inpArr)):
            for j in range(0,len(inpArr)-1-i):
                if inpArr[j]>inpArr[j+1]:
                    temp=inpArr[j]
                    inpArr[j]= inpArr[j+1]
                    inpArr[j+1]=temp

    def printSortArr(self,inpArr):
        for i in range(0, len(inpArr) - 1):
            print(inpArr[i])

    def callmergeSort(self,inpArr):
        self.mergeSort(inpArr,0,len(inpArr)-1)

    def mergeSort(self, inpArr, start, end):
        mid =(start +end)//2

        if start< mid:
            self.mergeSort(inpArr,start,mid)
            if mid+1 <end:
                self.mergeSort(inpArr,mid+1,end)

        #
        # if start == mid:
        #     print(f'left array is {inpArr[start]}')
        # else:
        #     print(f'left array is {inpArr[start:mid]}')
        #
        # if mid+1 == end:
        #     print(f'right array is {inpArr[mid+1]}')
        # else:
        #     print(f'right array is {inpArr[mid + 1:end]}')

        print(f'start is {start} , mid is {mid}, end is {end}')
        i=start
        j=mid+1
        tmpArr =[]

        while(i<=mid ):
            # print(f'left value is {inpArr[i]} and right value is {inpArr[mid+1]}')
            # if inpArr[i] >inpArr[mid+1]:
                # temp=inpArr[i]
                # inpArr[i] = inpArr[mid+1]
                # inpArr[mid + 1] = temp
            if j <=end and inpArr[i] >inpArr[j] :
                tmpArr.append(inpArr[j])
                j=j+1
            else:
                tmpArr.append(inpArr[i])
                i = i + 1
        while(len(tmpArr)<end-start+1):
            tmpArr.append(inpArr[j])
            j=j+1

        l=start
        length = len(tmpArr)
        for k in range(0,length):
            inpArr[l]=tmpArr[k]
            l=l+1


        # print(f'after merge temp array is :{tmpArr}')
        print(f'after merge array is :{inpArr}')



testVar = SortingAlgos()
inpArray =[ 9,2,32,19,181,-200,0,20,4,6,34,78,95,40,0,0,-32768]
inpArray =[ 0,0,0,0,0,0,-3,0,0,0,00,0,0,0,0,0,0,-2,0,000,]
inpArray =[ 10,9,8,7,6,5,4,3,2,1,0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10]
inpArray =[ 110,90,80,70,60,50,40,30,20,100,5000,-12345,1,2,3,4,5,6,7,8,9,10,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10]
print(type(inpArray))
print(inpArray)
#testVar.bubbleSort(inpArray)
testVar.callmergeSort(inpArray)
print("After sorting")
#print(inpArray)
testVar.printSortArr(inpArray)
print("""current value is:\
testing multi lines""")