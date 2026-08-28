def search(array: list[int], number: int) -> bool:
    left, right = 0, len(array) - 1
    while left <= right:
        mid = (left + right) // 2
        if array[mid] == number:
            return True
        elif array[mid] < number:
            left = mid + 1
        else:
            right = mid - 1
    return False
