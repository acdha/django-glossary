from django.test import TestCase
from django.core.urlresolvers import reverse

from glossary.models import Term, Synonym

class GlossaryTestCase(TestCase):
    def setUp(self):
        self.ace = Term.objects.create( title="Ace", slug = "ace", description="Description for Ace")
        self.base = Term.objects.create( title="Bace", slug = "base", description="Ace of BASE!")
        self.case = Term.objects.create( title="Case", slug = "case", description="Make a case")
        self.dace = Term.objects.create( title="Dace", slug = "dace", description="A dude named Dace")
        self.eco = Term.objects.create( title="Eco", slug = "eco", description="Eco-awesomeness")
        self.face = Term.objects.create( title="Face", slug = "face", description="In your face!")
        self.gale = Term.objects.create( title="Gale", slug = "gale", description="Dorothy Gale?")
        self.hail = Term.objects.create( title="Hail", slug = "hail", description="Hail of fail")
        self.ill = Term.objects.create( title="Ill", slug = "ill", description="That coat is ill.")
        self.synonym = Synonym.objects.create(title="Synonym", term = self.ace)

    def test_term(self):
        # These really aren't supposed to be different without non-ascii test data:
        self.assertEquals(str(unicode(self.ace)), str(self.ace))

        self.assertEquals(unicode(self.ace.title), u"Ace")
        self.assertEquals(self.ace.slug, "ace")

    def test_synonym(self):
        self.assertEquals(self.ace.title, self.synonym.term.title)

        # These really aren't supposed to be different without non-ascii test data:
        self.assertEquals(str(unicode(self.synonym)), str(self.synonym))

        self.assertTrue("synonym for" in unicode(self.synonym))
        self.assertTrue(self.ace.title in unicode(self.synonym))

    def test_term_view(self):
        response = self.client.get(reverse("glossary-list"))
        self.assertTrue(response.status_code == 200)

        response = self.client.get(self.ace.get_absolute_url())
        self.assertTrue(response.status_code == 200)
        self.assertContains(response, "Ace")
        self.assertContains(response, "Description for Ace")
        self.assertContains(response, self.ace.title)
        self.assertContains(response, self.ace.description)
        self.assertContains(response, self.synonym.title)

        response = self.client.get(reverse("glossary-list") + '?l=a')
        self.assertTrue(response.status_code == 200)
        self.assertContains(response, '<li class="current"><a href = "?l=a">a</a></li>')

        response = self.client.get(reverse("glossary-list") + '?q=dude')
        self.assertTrue(response.status_code == 200)
        self.assertContains(response, "Dace")
        self.assertContains(response, '<input type="text" name="q" id="id_q" value="dude"')

