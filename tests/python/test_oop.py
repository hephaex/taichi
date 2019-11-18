import taichi as ti

@ti.host_arch
def test_oop():
  class Array2D:
    def __init__(self, n, m, increment):
      self.n = n
      self.m = m
      self.val = ti.var(ti.f32)
      self.total = ti.var(ti.f32)
      self.increment = increment

    def place(self, root):
      root.dense(ti.ij, (self.n, self.m)).place(self.val)
      root.place(self.total)

    @ti.classkernel
    def inc(self: ti.template()):
      for i, j in self.val:
        ti.atomic_add(self.val[i, j], self.increment)

    @ti.classkernel
    def reduce(self: ti.template()):
      for i, j in self.val:
        ti.atomic_add(self.total, self.val[i, j] * 4)

  arr = Array2D(128, 128, 3)

  @ti.layout
  def place():
    ti.root.place(arr)
    ti.root.lazy_grad()

  arr.inc()
  arr.inc(__gradient=True)
  assert arr.val[3, 4] == 3
  arr.inc()
  assert arr.val[3, 4] == 6

  with ti.Tape(loss=arr.total):
    arr.reduce()

  for i in range(arr.n):
    for j in range(arr.m):
      assert arr.val.grad[i, j] == 4
