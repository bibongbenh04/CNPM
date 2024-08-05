n, m = map(int, input().split())

if n > m:
    for i in range(n, m - 1, -1):
        print(i, end=' ')
elif n < m:
    for i in range(m, n - 1, -1):
        print(i, end=' ')
else:
    print("Gia tri cua n va m bang nhau", end = ' ')