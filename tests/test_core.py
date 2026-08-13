
from forgemind.core import Node,run,evolve,canon
def test_compose():
    p=[Node("U","rev"),Node("U","neg")]
    assert run(p,[1,-2,3])==[-3,2,-1]
def test_param():
    assert run([Node("P","add",2)],[1,3])==[3,5]
def test_deterministic():
    assert evolve(5,[Node("U","rev")],8,25)[1]==evolve(5,[Node("U","rev")],8,25)[1]
