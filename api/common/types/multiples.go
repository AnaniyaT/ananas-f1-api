package types

type Pair[T any, U any] struct {
	First  T
	Second U
}

func NewPair[T any, U any](first T, second U) Pair[T, U] {
	return Pair[T, U]{First: first, Second: second}
}

type Triple[T any, U any, V any] struct {
	First  T
	Second U
	Third  V
}

func NewTriple[T any, U any, V any](first T, second U, third V) Triple[T, U, V] {
	return Triple[T, U, V]{First: first, Second: second, Third: third}
}
