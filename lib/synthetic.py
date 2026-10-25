PEOPLE = ('Alice', 'Bob', 'Carol', 'David')
BOXES = ('A', 'B', 'C', 'D')
COLORS = ('red', 'blue', 'green', 'yellow')

def prompts(mapping, colors, person_order, box_order, person):
    box = mapping[person]
    prefix = 'Use only the facts in this scenario.\n\n'
    prefix += ''.join((f'Box {b} contains {colors[b]}.\n' for b in box_order))
    prefix += ''.join((f'{p} has box {mapping[p]}.\n' for p in person_order))
    return {'person_box': prefix + f'\nQuestion: Which box does {person} have?\nAnswer: box', 'box_color': prefix + f'\nQuestion: What color is in box {box}?\nAnswer:', 'two_hop': prefix + f"\nQuestion: What color is in {person}'s box?\nAnswer:"}
