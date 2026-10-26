# Official upstream synchronization

Source: [hitokoto-osc/sentences-bundle](https://github.com/hitokoto-osc/sentences-bundle), branch master.
Imported upstream commit: c169bae5faed220a7026b3b397f153f2dc2b2af8.

## Import policy

- Retain the existing four-field format: hitokoto, type, from, from_who.
- Retain all original 938 records in order, including 300 custom records; append approved new records.
- Include new sentences for existing works, explicitly matched watched works, and the 31 manually selected source names below.
- Exclude the remaining unselected sources. Remove only exact duplicates among newly imported records.
- Keep reviewed additions in upstream-selected.json; python3 gen.py reproduces cat.json.
- Record exact source names and selection codes in upstream-selection.json.
- Rebase the fork commits onto the latest upstream/master, then restore the exact reviewed fork tree. Upstream ancestry is retained while the customized API, file layout and selected data remain authoritative.

## Manual selections

| Code | Official source |
| --- | --- |
| A014 | 紫罗兰永恒花园 |
| A018 | 狼与香辛料 |
| A033 | Re：从零开始的异世界生活 |
| A040 | 熊出没 |
| A041 | 罪恶王冠 |
| A057 | 海绵宝宝 |
| A060 | 功夫熊猫 |
| A062 | 小林家的龙女仆 |
| A064 | 机动战士高达 |
| A069 | 紫罗兰的永恒花园 |
| A073 | My Little Pony: Friendship is Magic |
| A074 | Re:从零开始的异世界生活 |
| A083 | 如果有个妹妹就好了 |
| A107 | 少女终末旅行 |
| A110 | 新世纪福音战士 |
| A113 | 来自风平浪静的明天 |
| A115 | 死亡笔记 |
| A122 | 葬送的芙莉莲 |
| A129 | Ave Mujica |
| A136 | TARI TARI |
| A138 | ラブライブ！ |
| A195 | 莉可丽丝 |
| B017 | 葬送的芙莉莲 |
| B004 | 少女终末旅行 |
| B033 | 咒术回战 |
| C014 | Stellaris |
| C026 | 三色绘恋 |
| C030 | 群星 |
| C062 | 黑神话悟空 |
| C073 | Phigros |
| C074 | phigros |

## Result

- Automatically selected source names: 185.
- Manually selected source names: 31.
- New sentences in the manual selection: 144.
- Total imported additions: 428.
- Final catalog size: 1366.
