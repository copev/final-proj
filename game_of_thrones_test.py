import unittest
import game_of_thrones_proj as got


class Test_Attributes(unittest.TestCase):
    def setUp(self):
        self.site_valar = got.make_episode_instance('https://www.imdb.com/title/tt2112510/')
        self.site_blackwater = got.make_episode_instance('https://www.imdb.com/title/tt2084342/')

    def test_ep_name(self):
        self.assertEqual(self.site_valar.episode_name, "Valar Morghulis")
        self.assertEqual(self.site_blackwater.episode_name, "Blackwater")

    def test_season(self):
        self.assertEqual(self.site_valar.season, "Season 2")
        self.assertEqual(self.site_blackwater.season, "Season 2")

    def test_episode_number(self):
        self.assertEqual(self.site_valar.episode_number, "Episode 10")
        self.assertEqual(self.site_blackwater.episode_number, "Episode 9")

    def test_rating(self):
        self.assertEqual(self.site_valar.rating, "9.4")
        self.assertEqual(self.site_blackwater.rating, "9.7")

    def test_length(self):
        self.assertEqual(self.site_valar.ep_length, "1h 4min")
        self.assertEqual(self.site_blackwater.ep_length, "55min")



if __name__ == '__main__':
    unittest.main()