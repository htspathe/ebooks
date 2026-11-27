import tempfile
import unittest
from pathlib import Path
from generate_activities import DOTS, MAZES, WORD_SEARCHES, generate_maze, make_word_search, polygon_samples, build

class ActivityGeneratorTests(unittest.TestCase):
    def test_all_maze_paths_are_valid(self):
        for page,size,_ in MAZES:
            walls,path=generate_maze(size,20261127+page)
            self.assertEqual(path[0],0); self.assertEqual(path[-1],size*size-1)
            self.assertEqual(len(path),len(set(path)))
            for a,b in zip(path,path[1:]):
                ar,ac=divmod(a,size); br,bc=divmod(b,size)
                self.assertEqual(abs(ar-br)+abs(ac-bc),1)
                wi=0 if br==ar-1 else 1 if bc==ac+1 else 2 if br==ar+1 else 3
                self.assertFalse(walls[a][wi])
    def test_dot_counts_and_unique_positions(self):
        for page,name,count,outline in DOTS:
            pts=polygon_samples(outline,count)
            self.assertEqual(len(pts),count,(page,name))
            self.assertEqual(len(set((round(x,5),round(y,5)) for x,y in pts)),count)
    def test_every_word_is_placed(self):
        for page,title,words,diagonal in WORD_SEARCHES:
            grid,placements=make_word_search(words,diagonal,20261127+page)
            self.assertEqual(len(grid),10); self.assertTrue(all(len(row)==10 for row in grid))
            self.assertEqual({p["word"] for p in placements},set(words))
            for p in placements:
                dr,dc=p["direction"]; r,c=p["start"]
                self.assertEqual("".join(grid[r+i*dr][c+i*dc] for i in range(len(p["word"]))),p["word"])
    def test_build_emits_exact_page_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=build(Path(tmp))
            self.assertEqual(report["status"],"GENERATED_NEEDS_VISUAL_REVIEW")
            self.assertEqual(report["pages_generated"],list(range(15,55))+list(range(73,81)))
            self.assertEqual(len(list(Path(tmp).rglob("*.svg"))),48)

if __name__=="__main__": unittest.main()
