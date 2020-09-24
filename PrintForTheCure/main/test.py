def main():
    teststr = "agfsfg"
    stringBAD = "These would be used by dentists, dental assistants and hygienists who are treating emergency covid + patients who are experiencing emergent dental pain and require treatment as well as routine dental patients during the pandemic. We are not “near by” covid patients, we are LITERALLY IN THIER MOUTHS. This would be amazing if someone would print those for us!! PLEASE CONSIDER YOUR DENTAL CARE PROVIDERS AS THEY GET OVERLOOKED BY ALL THE FRONTLINE HEALTHCARE GIVE AWAYS, GIFTS AND DISCOUNTS!! %s" % teststr
    stringGOOD = "I am typing a lot of sentences and how are you doing today this is really random but there are no \"ASCII\" chars in here."
    removeASCII(stringBAD)
    removeASCII(stringGOOD)

def removeASCII(s):
    print("string: " + str(all(ord(c) < 128 for c in s)))
    for i in range(len(s)):
        if ord(s[i]) > 128:
            s = s[:i] + ' ' + s[i + 1:]
    print(s)

if __name__ == "__main__":
    main()
