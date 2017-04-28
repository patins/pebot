# pebot
A bot that registers you for your required MIT PE class so you don't have to wake up at 8 AM.
No longer works cause of Duo two factor auth, and I finished my PE requirements so why not release it

## What it looks like when it works
``
2016-03-02 07:59:53,046 "GET /mitpe/student/registration/sectionList HTTP/1.1" 200 None
2016-03-02 07:59:53,136 Got date 01/27/2016
2016-03-02 07:59:58,141 Resetting dropped connection: edu-apps.mit.edu
2016-03-02 07:59:58,898 "GET /mitpe/student/registration/sectionList HTTP/1.1" 200 None
2016-03-02 07:59:58,993 Got date 01/27/2016
2016-03-02 08:00:03,998 Resetting dropped connection: edu-apps.mit.edu
2016-03-02 08:00:23,544 "GET /mitpe/student/registration/sectionList HTTP/1.1" 200 None
2016-03-02 08:00:23,656 Found section {'section_id': '2926424612092F0F0000015333540E28', 'days': 'TR', 'time': '1:00 PM', 'title': 'Archery', 'activity': 'Individual Sports'}
2016-03-02 08:00:23,658 Resetting dropped connection: edu-apps.mit.edu
2016-03-02 08:00:25,738 "POST /mitpe/student/registration/create HTTP/1.1" 302 None
2016-03-02 08:00:25,745 Resetting dropped connection: edu-apps.mit.edu
2016-03-02 08:00:25,926 "GET /mitpe/student/registration/home HTTP/1.1"
``
