"""Apply source-close clause-restoration corrections for MADOran Batch 18."""
from __future__ import annotations

import json
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(__file__).rsplit("\\scripts\\", 1)[0])

from scripts import correct_madoran_enrichment_batch14_correction02 as engine
from scripts.build_madoran_enrichment_batch18 import BATCH_OUT
from scripts.build_madoran_enrichment_scaffold import ROOT

BASE_COMMIT = "565e5d6"
BATCH_ID = "MADORAN-ENRICH-018"
CORRECTION_ID = "MADORAN-ENRICH-018-CORRECTION-02"
PROMPT_VERSION = "madoran-source-enrichment-v18-correction-2"
BATCH_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_qa.json"
CORRECTION_QA_OUT = ROOT / "data/master/qa/madoran_enrichment_batch18_correction02_qa.json"
EVIDENCE_PATH = "data/master/qa/madoran_enrichment_batch18_correction02_qa.json"
PROVENANCE_BEFORE = 15854

CORRECTIONS = {
    1090: {
        "english": "The speaker says, ‘I will tell you and make you understand: I am taking you to ghwla. Beware if you speak; I will sell you.’ The listener is then addressed as selling the speaker while the speaker will not speak. The speaker says, ‘You all betray people and sell them, and we will not speak,’ then keeps the opaque harja and bwia surfaces: outside or at my father’s place. The Sons of the Day will make them pay dearly; the speaker will still betray and sell, says ‘your right—rejoice,’ and says they will make the listener live with ghwla in bliss. They say they lived well with the Sons of the Day, that you all brought them here, and finish, ‘I am telling you: be quiet, go away.’ All turns and actor directions are retained.",
        "korean": "화자는 ‘너에게 말하고 이해시키겠다. 나는 너를 ghwla에게 데려간다. 조심해, 네가 말하면 내가 너를 팔겠다’고 해요. 이어 상대가 화자를 팔고 화자는 말하지 않겠다는 방향을 보존해요. ‘너희는 사람들을 배신하고 팔며 우리는 말하지 않겠다’고 하고 harja와 bwia의 불투명한 표면, 즉 밖 또는 아버지 쪽이라는 표현을 그대로 둬요. 울라드 나하르가 대가를 비싸게 치르게 할 것이며 계속 배신하고 팔겠다고 하고, ‘네 권리야, 기뻐해’라고 말한 뒤 상대를 ghwla와 함께 نعيم, 즉 행복 속에서 살게 하겠다고 해요. 울라드 나하르와 함께 잘 살았다고 하고 너희가 자신을 여기로 데려왔다고 말한 뒤 ‘내가 너에게 말하니 조용히 하고 가라’고 끝내며 모든 turn과 행위자 방향을 보존해요.",
    },
    1091: {
        "english": "The speaker says, ‘We are bringing you merchandise. What is wrong with you, you sh7ma of the earth, going and coming at me, doubters?’ The wording remains partly opaque. They say, ‘I brought you the merchandise of my life, and I bring you merchandise,’ then say that this one commodity speaks by itself, talks by itself, and is a good commodity—glory be to God. The self-speaking surface is retained without adding movement.",
        "korean": "화자는 ‘우리가 너에게 상품을 가져온다. 너 왜 그래, 이 땅의 sh7ma야? 나에게 왔다 갔다 하며 의심하느냐?’라고 해요. 이 표현의 일부는 불투명한 채로 둬요. 이어 ‘내 삶의 상품을 너에게 가져왔고 상품들을 가져온다’고 한 뒤, 이 상품 하나는 혼자 말하고 스스로 이야기하며 좋은 상품이라고 해요. ‘하느님께 찬미를’이라는 끝맺음도 보존하고 물건이 움직인다는 내용을 추가하지 않아요.",
    },
    1094: {
        "english": "The speaker says, ‘This nz9i—I use it with it; take it from me, take it from me,’ preserving the uncertain nz9i surface and the repeated dih 3lia direction. They ask for only ten doro for it, say they will give nothing, say it did not want to, and then say, ‘Come on, fine, give us eight doro for it.’",
        "korean": "화자는 불확실한 nz9i 표면을 유지하며 ‘이 nz9i를 그것과 함께 쓴다. 내게서 가져가, 내게서 가져가’라고 반복해요. 반복되는 dih 3lia의 ‘내게서 가져가’ 방향을 보존해요. 이것에 10도라만 달라고 하고 아무것도 주지 않겠다고 하며 그것이 원하지 않았다고 말한 뒤 ‘어서, 좋아, 이것에 8도라를 줘’라고 해요.",
    },
    1100: {
        "processing_flags": "code_switching|long_source|source_ambiguity",
    },
    1102: {
        "english": "The speaker tells the listener not to repeat this talk and says, ‘Last time they gave me fiza.’ They will not meet the listener, but will meet this ghwla and lizandian. The speaker says, ‘Look, follow me,’ and curses this work or service. The last-time actor and direction are preserved.",
        "korean": "화자는 상대에게 이 말을 되풀이하지 말라고 하며 ‘지난번에는 그들이 내게 fiza를 줬어’라고 해요. 상대는 만나지 않지만 이 ghwla와 lizandian을 만나겠다고 해요. ‘봐, 나를 따라와’라고 하고 이 일이나 서비스를 저주하며, 지난번이라는 시간과 행위자 방향을 보존해요.",
    },
    1103: {
        "english": "The speaker says, ‘They brought you, as they brought you; they did not bring me.’ The speaker says they told them, ‘Come take me,’ made a rendez-vous with them, and repeated, ‘Come take me.’ They ask the listener to listen and explain that the people of the listener’s village think, ‘We took you,’ although ‘we did not take you.’ The speaker keeps the opaque cowboy clause about being able to evade them. For the listener’s sake, the speaker took a risk and came yesterday; they were put in a sewer or drain, and the cold, hunger, and thirst killed them, followed by ‘you deserve it.’ The repeated turns and actors are all retained.",
        "korean": "화자는 ‘그들이 너를 데려왔어, 너를 데려온 것처럼. 그들은 나를 데려오지 않았어’라고 해요. 화자는 그들에게 ‘와서 나를 데려가라’고 말했고 rendez-vous를 했으며 다시 ‘와서 나를 데려가라’고 했다고 해요. 상대에게 잘 들으라고 하면서 상대 마을 사람들이 ‘우리가 너를 데려갔다’고 생각하지만 ‘우리는 너를 데려가지 않았다’고 설명해요. 자신이 그들을 피할 수 있다는 불투명한 cowboy 절도 표면으로 보존해요. 상대 때문에 위험을 감수하고 어제 왔으며, 하수구나 배수로에 가둬져 추위·배고픔·갈증이 자신을 죽였다고 하고 ‘네가 그럴 만하다’고 끝내요. 반복 turn과 행위자를 모두 보존해요.",
        "processing_flags": "cefr_boundary|code_switching|long_source|source_ambiguity",
    },
    1105: {
        "english": "The speaker says, ‘I grew a moustache, my brother, so that you would not recognize or remember me, yes?’ preserving the second-person bash mtn39lsh direction rather than making it a first-person failure to understand. They then address a son: ‘My child, do it with Boujadia as you did not do it with us.’",
        "korean": "화자는 ‘형제야, 네가 나를 알아보거나 기억하지 못하게 하려고 콧수염을 길렀어, 그렇지?’라고 하며 bash mtn39lsh의 2인칭 방향을 보존해요. 이를 화자가 이해하지 못한다는 1인칭 표현으로 바꾸지 않아요. 이어 아들에게 ‘얘야, Boujadia와 해. 너희가 우리와는 그렇게 하지 않았잖아’라고 해요.",
    },
    1106: {
        "english": "The speaker tells someone to raise their hands and look at the speaker well, confirms ‘yes, za3bata,’ and asks where the listener’s friend is. The friend is in the forest hunting and said, ‘I am in the valley; I am hunting.’ The speaker does not know what the friend is doing or whether the friend is working for himself. The speaker says, ‘As for me, I am not working; I am rwbw today,’ preserving the repos or day-off-like surface, then says they came to stroll a little today, here. The exchange continues: ‘Good morning, za3bata; pull your grandfather—are you saying you crave a cat with seven lives at your place?’ The hunting, work, day-off, and final cat clauses remain separate.",
        "korean": "화자는 상대에게 손을 들고 자신을 잘 보라고 하며 ‘그래, za3bata’라고 확인하고 상대의 친구가 어디 있는지 물어요. 친구는 숲에서 사냥 중이고 ‘나는 계곡에 있어, 사냥하고 있어’라고 말했다고 해요. 화자는 친구가 무엇을 하는지, 자기 일을 하는지 모른다고 해요. 화자는 ‘나는 일하지 않아. 오늘은 rwbw야’라고 하며 휴무나 repos처럼 들리는 표면을 로봇으로 확정하지 않아요. 이어 ‘오늘 여기 잠깐 산책하러 왔어’라고 하고, ‘좋은 아침이야, za3bata. 네 할아버지를 끌어내라—네가 있는 곳에 목숨이 일곱 개인 고양이를 그리워한다고 말하는 거야?’라는 후반 turn을 보존해요. 사냥·일·휴무·고양이 절을 합치지 않아요.",
        "processing_flags": "cefr_boundary|code_switching|long_source|source_ambiguity",
    },
    1108: {
        "english": "The speaker says, ‘Yes, indeed, I was distracted for five minutes. You all killed someone; we told you that bullets are forbidden here.’ The plural actor and the warning that bullets are forbidden here are preserved.",
        "korean": "화자는 ‘그래, 정말로 나는 5분 동안 정신이 팔려 있었어. 너희 모두가 한 사람을 죽였고, 우리는 너희에게 여기서는 총알이 금지라고 말했어’라고 해요. 복수 행위자와 이곳에서 총알이 금지된다는 경고를 보존해요.",
    },
    1109: {
        "english": "The speaker says there was nobody who saw the weddings and asks or tells the listeners to see them; then says it is normal to see them and that they see them in the month of Ramadan. The speaker ends, ‘None of you know anything.’ The repeated shaf/tshwfwhm visibility structure and l3ras surface are retained.",
        "korean": "화자는 결혼식 또는 l3ras를 본 사람이 없었다고 하면서 상대들에게 그것을 보라고 해요. 이어 그것을 보는 것은 괜찮고 라마단 달에 그것을 본다고 말한 뒤 ‘너희는 아무것도 알지 못해’라고 끝내요. shaf/tshwfwhm의 반복되는 보기·보지 못하기 구조와 l3ras 표면을 보존해요.",
    },
    1110: {
        "english": "The speaker asks, ‘Who knocked this person down?’ and says, ‘By God, I do not know, my brother; I was inside, distracted.’ They say, ‘Every three days I see someone knocked down here.’ They then say they did not see and remained distracted inside. The three-day frequency, the lying or knocked-down person, and the surrounding turns are preserved.",
        "korean": "화자는 ‘누가 이 사람을 쓰러뜨렸어?’라고 묻고 ‘하느님께 맹세코 모르겠어, 형제야. 나는 안에 있었고 정신이 팔려 있었어’라고 해요. 이어 ‘나는 3일마다 여기서 누군가 쓰러져 있는 것을 봐’라고 하며 kl 3 jwgh의 3일 빈도를 보존해요. 그 뒤 보지 못했고 안에서 계속 정신이 팔려 있었다고 해 주변 turn을 모두 보존해요.",
    },
    1111: {
        "english": "The speaker says, ‘You do not see anything. I work and come; I meet people when I break or wear myself out,’ retaining the uncertain n9t3 rw7i surface. They then ask, ‘Why do you not have a registre du commerce?’ The French registre du commerce clause and the preceding work and meeting clauses are all retained.",
        "korean": "화자는 ‘너는 아무것도 보지 못해. 나는 일하고 오며, 나를 소모하거나 지치게 할 때 사람들을 만나’라고 하며 불확실한 n9t3 rw7i 표면을 보존해요. 이어 ‘왜 너에게 registre du commerce가 없지?’라고 물어요. 프랑스어 registre du commerce 절과 앞의 일·만남 절을 모두 보존해요.",
    },
    1112: {
        "english": "The speaker says, ‘You are not paying lizambwa, the les impôts or taxes.’ They then say, ‘Stay as you are; I will bring a forensic doctor.’ The taxes surface and the stay-as-you-are and forensic-doctor clauses are retained.",
        "korean": "화자는 ‘너는 lizambwa, 즉 les impôts와 세금을 내지 않고 있어’라고 해요. 이어 ‘네가 있는 그대로 있어. 내가 법의학 의사를 데려올게’라고 해요. 세금 표면과 그대로 있으라는 절, 법의학 의사를 데려오겠다는 절을 보존해요.",
    },
    1113: {
        "english": "The speaker says, ‘By God, I do not know you at all. Tomorrow I will change jobs.’ They address Moulkheir: ‘Free yourself; come on, free me with you.’ They say, ‘We are playing. Shall I free you?’ The release directions, the job-change clause, Moulkheir vocative, and final question are retained.",
        "korean": "화자는 ‘하느님께 맹세코 나는 너희를 전혀 몰라’라고 하고 ‘내일 직업을 바꿀 거야’라고 해요. Moulkheir에게 ‘스스로 풀려나. 어서, 나도 너와 함께 풀어 줘’라고 말해요. 이어 ‘우리는 놀고 있어. 내가 너를 풀어 줄까?’라고 하며 해방의 방향, 직업 변경, Moulkheir 호칭과 마지막 질문을 보존해요.",
    },
    1114: {
        "english": "The speaker says, ‘Yes, are you not clever or alert? I came for your sake.’ They ask, ‘Are you not the one who wants to make it disappear from the cowboys?’ Then they say, ‘I wanted to make it disappear for them, but I came for your sake.’ The listener direction, the opaque kwbwiz/cowboys surface, and all clauses are retained.",
        "korean": "화자는 ‘그래, 너는 영리하거나 눈치가 빠르지 않니? 나는 너 때문에 왔어’라고 해요. 이어 ‘너는 그것을 cowboys에게서 사라지게 하려던 사람이 아니야?’라고 묻고 ‘나는 그것을 그들에게서 사라지게 하고 싶었지만 너 때문에 왔어’라고 해요. 상대를 향한 방향, 불투명한 kwbwiz/cowboys 표면과 모든 절을 보존해요.",
    },
    1115: {
        "english": "The speaker says, ‘I will not free you; free yourself.’ They continue, ‘Why? Shame on you; may your heart remain good.’ Finally they say, ‘Just a little—let us hear a howling or wailing sound.’ The reproach, good-heart clause, and 3wawaa sound surface are retained.",
        "korean": "화자는 ‘내가 너를 풀어 주지 않을 테니 네가 스스로 풀려나라’고 해요. 이어 ‘왜? 부끄러운 줄 알아. 네 마음에 선함이 있기를 바라’고 하고, 마지막으로 ‘조금만, 우리가 울부짖는 소리를 듣게 해 줘’라고 해요. 질책·선한 마음·3wawaa 소리 표면을 모두 보존해요.",
    },
    1119: {
        "english": "The speaker says, ‘I did not play with dogs at all. You do not give them anything to eat or drink; because of you I lost the hunt.’ They say, ‘I want to ask you—come. These three days, where were you?’ Then they retort, ‘Ah, until now, when did you know that I am your son?’ and repeat, ‘Until now you ask? These three days, where were you?’ The dog food and water, lost hunt, invitation, and repeated three-day question are retained.",
        "korean": "화자는 ‘나는 개들과 전혀 놀지 않았어. 너는 그들에게 먹을 것도 마실 것도 주지 않잖아. 너 때문에 사냥을 망쳤어’라고 해요. 이어 ‘너에게 묻고 싶어, 와. 이 3일 동안 어디에 있었어?’라고 하고, ‘아, 이제야 네가 내가 네 아들이라는 것을 언제 알았어?’라고 되물어요. 마지막으로 ‘이제야 묻는 거야? 이 3일 동안 어디에 있었어?’라고 반복하며 개의 먹이·물, 사냥을 망친 원인, 초대와 3일 질문을 모두 보존해요.",
    },
    1121: {
        "english": "The speaker says, ‘Some people took me and tied me; I do not know them at all. They took me.’ They add, ‘Yes, they lodged me in a sewer. I have spent three days without dinner or breakfast at your place; what they did to me left me diminished or lacking.’ The detention, unknown actors, sewer, and food-deprivation clauses are retained; w7din is not changed into a simple statement that some people do not understand.",
        "korean": "화자는 ‘어떤 사람들이 나를 데려가 묶었어. 나는 그들을 전혀 몰라. 그들이 나를 데려갔어’라고 해요. 이어 ‘그래, 그들이 나를 하수구나 배수로에 가뒀어. 나는 네 집에서 3일 동안 저녁도 아침도 먹지 못했어. 그들이 내게 한 일 때문에 내가 부족해졌어’라고 하며, w7din을 단순히 ‘어떤 사람들이 이해하지 못한다’는 말로 바꾸지 않아요. 구금·불명확한 행위자·하수구·식사 박탈 절을 보존해요.",
    },
    1122: {
        "english": "The speaker says, ‘You are not my father; clearly, you are not my father.’ The same speaker continues, ‘Fine, do not cry. Now let us understand with them,’ preserving the direction of dwk ntafhm m3ahm without inventing a friend as a new speaker.",
        "korean": "화자는 ‘너는 내 아버지가 아니야. 분명히 너는 내 아버지가 아니야’라고 해요. 같은 화자가 이어 ‘좋아, 울지 마. 이제 그들과 함께 이해하자’고 하며 dwk ntafhm m3ahm의 방향을 보존하고 새로운 친구 화자를 만들어내지 않아요.",
    },
    1123: {
        "english": "The speaker says it appears they were brought only to the listener’s place. Then: ‘Here she comes—look.’ They tell someone to be quiet, bring in your daughter, and give her a little fenugreek. The shaf surface is kept as ‘look’ rather than being made into a chief or person name.",
        "korean": "화자는 자신이 상대의 집에만 데려와진 것처럼 보인다고 해요. 이어 ‘여기 그녀가 온다, 봐’라고 하며 shaf를 우두머리나 사람 이름으로 만들지 않아요. 누군가에게 조용히 하라고 하고 네 딸을 안으로 데려와 딸에게 호로파를 조금 주라고 해요.",
    },
    1125: {
        "english": "The speaker says, ‘I am talking to you all; come on, go.’ They call the listener: ‘Come here, in front, and say Juventus—how much did they score yesterday?’ The response is, ‘They did zero-zero, look.’ The opening commands, address, score question, and zero-zero answer are retained.",
        "korean": "화자는 ‘너희에게 말하고 있어. 어서 가’라고 하고 상대를 부르며 ‘여기 앞으로 와서 Juventus가 어제 몇 점을 냈는지 말해’라고 해요. 대답은 ‘0 대 0이었어, 봐’예요. 초두 명령·호명·점수 질문·0 대 0 답변을 보존하고 질문 중심 화행으로 정리해요.",
        "speech_act": "question",
    },
    1127: {
        "english": "The speaker speaks for the sake of the assembled group present tonight and for loved ones, saying not to forget to go out or act for the friend’s sake. They say, ‘Oh, I forgot—for the sake of my right arm, which I do not forget and which does not leave my mind.’ They continue with the grandfather and strong-vein surfaces: a red vein, contra on the shinin or related opaque surface, and lizabaj, ending with ‘May God replace it and bless health.’ All group, friend, right-arm, vein, contra, and blessing clauses remain visible.",
        "korean": "화자는 오늘 밤 모인 사람들과 사랑하는 사람들을 위해 말하며 친구를 위해 나가거나 행동하는 것을 잊지 말라고 해요. ‘아, 그리고 잊었어. 내가 잊지 않고 마음에서 떠나지 않는 내 오른팔을 위해서’라고 말해요. 이어 할아버지와 강한 혈관 표면, 붉은 혈관, shinin 또는 그와 관련된 불투명한 표면에 대한 contra, lizabaj를 말하고 ‘하느님이 대신해 주시고 건강에 복을 주시기를’이라고 끝내요. 집단·친구·오른팔·혈관·contra·축복 절을 모두 보존해요.",
    },
    1128: {
        "english": "The speaker says, ‘I will give you a poem for your sake and for the sake of the loved ones who outdid or left you by night and by trick. Listen to what a poet says in his words.’ They then recite the opaque refrain 7ai7aia: it tires, it is not—then it is a 7i7aia; only when the hunt rises do they not kill it. The poem, friend clause, poet, refrain, and kill-negation hunting clause are retained without forcing the opaque word.",
        "korean": "화자는 ‘너를 위해, 그리고 밤에 너를 앞서거나 속임수로 떠난 사랑하는 사람들을 위해 시 한 편을 줄게. 시인이 말하는 것을 들어’라고 해요. 이어 불투명한 7ai7aia 후렴을 읊어요. 그것은 지치고, 그것은 아니며, 다시 7i7aia라고 하고, 사냥이 일어날 때에만 그것을 죽이지 않는다고 해요. 시·친구 절·시인·후렴·사냥과 살해 부정 절을 억지로 확정하지 않고 보존해요.",
    },
    1129: {
        "english": "The speaker says that those who are passionate about hunting come directly or face-to-face. They are awake from worries and cannot endure, and the speaker adds ‘for the sake of zghratat,’ retaining zghratat as a ululation or celebratory surface. The hunting-enthusiast, worry, endurance, and ululation clauses are all present.",
        "korean": "화자는 사냥에 열중하는 사람들이 직접 또는 마주 보고 온다고 해요. 그들은 걱정에서 깨어 있지만 견디지 못한다고 하고 ‘zghratat를 위해서’라고 덧붙여요. zghratat를 축하의 울음소리나 ululation 표면으로 보존하며 사냥 애호가·걱정·견딤·울음소리 절을 모두 남겨요.",
    },
    1131: {
        "english": "The speaker says, ‘You searched or turned it over for artists. Who killed this one? I did not see him. You did not see anything either. I am in the kitchen; I did not see.’ The artists, killing question, repeated not-seeing clauses, and flkwzina kitchen surface are retained.",
        "korean": "화자는 ‘너희가 예술가들을 찾아보거나 그 일로 뒤졌어. 누가 이 사람을 죽였지? 나는 그를 보지 못했어. 너도 아무것도 보지 못했어. 나는 주방에 있었고 보지 못했어’라고 해요. 예술가·살해 질문·반복되는 보지 못했다는 절과 flkwzina의 주방 표면을 보존해요.",
    },
    1132: {
        "english": "The speaker says that life is not pleasing and mentions the lock or key of the door in an opaque clause. They say, ‘I am watching, 9ada. I will tell you one thing: when you see Madam, please ask her for one under 10,000 doro; do not ask for anything at all.’ They finish, ‘Are you listening to me or not?’ The amount, door/life surface, request to Madam, and listening question are retained.",
        "korean": "화자는 삶이 만족스럽지 않다고 하고 문 자물쇠나 열쇠에 관한 불투명한 절을 말해요. ‘나는 보고 있어, 9ada. 한 가지 말할게. Madam을 보면 그녀에게 10,000도라 아래의 것을 하나 요청해 줘. 아무것도 요청하지 마’라고 해요. 마지막으로 ‘내 말을 듣고 있어, 아니야?’라고 하며 금액·문과 삶의 표면·Madam에게 하는 요청·듣기 질문을 보존해요.",
    },
    1134: {
        "english": "The speaker says, ‘I am coming. The place is empty. Listen, take care of the other one, and I will take care of that man with the black chapeau.’ The final khladr ma alghalia surface remains uncertain and is not fixed as expensive. Arrival, empty-place, listening, division of roles, and the black-hat man remain in the row.",
        "korean": "화자는 ‘내가 가고 있어. 장소가 비어 있어. 들어 봐, 다른 사람을 돌봐. 나는 저 검은 샤포를 쓴 남자를 돌볼게’라고 해요. 마지막 khladr ma alghalia 표면은 불확실한 채로 두고 ‘비싸다’로 확정하지 않아요. 도착·빈 장소·듣기·역할 분담·검은 모자 남자를 모두 보존해요.",
    },
    1135: {
        "english": "The speaker addresses the listener through the opaque khladr/alshr surface and asks what the listener is doing with the tents. They say, ‘All day you are in the tents, you are in the bathroom, and you are one of us.’ They repeat, ‘Shut your mouth. Shut it.’ The tents, bathroom, belonging, and repeated bl3i fmk commands are retained.",
        "korean": "화자는 불투명한 khladr/alshr 표면으로 상대에게 말하며 상대가 천막에서 무엇을 하는지 물어요. ‘하루 종일 너는 천막에 있고, 욕실에 있고, 너는 우리 중 하나야’라고 해요. 이어 ‘입 다물어. 닫아’라고 반복하며 천막·욕실·소속·반복되는 bl3i fmk 명령을 보존해요.",
    },
    1137: {
        "english": "The speaker says, ‘Perhaps Madam rented you the accommodation.’ They brought her only a little drink, knowing that she is fasting these days. They say they thought they would come to check on her, that the poor woman has nobody, and that it is only the speaker who comes to check on her. The speaker ends, ‘How are you, sir?’ All drink, fasting, visit, isolation, and final greeting clauses are retained.",
        "korean": "화자는 ‘아마 Madam이 너희에게 숙소를 빌려 준 것 같아’라고 해요. 그녀가 요즘 금식 중인 것을 알면서 음료를 조금 가져다주었고, 그녀를 보러 오겠다고 생각했다고 해요. 불쌍한 그녀에게 아무도 없으며 그녀를 보러 오는 사람은 자신뿐이라고 말한 뒤 ‘어떻게 지내세요, 선생님?’이라고 끝내요. 음료·금식·방문·고립·마지막 인사 절을 모두 보존해요.",
    },
    1138: {
        "english": "The speaker says, ‘Forgive me, Sheikh of the Sons of the Day tribe. I wronged you, and it is my fault. But, especially, it was not me; Flitsha is the one who deceived me. I said your people did it to us, like enemies, and they wanted to set fire between us—the fitna.’ The apology, fault, actor direction, hostile act, and fitna clauses are retained.",
        "korean": "화자는 ‘울라드 나하르 부족의 셰이크여, 나를 용서해. 내가 당신에게 잘못했고 그것은 내 잘못이야. 하지만 특히 그건 내가 아니야. 나를 속인 사람은 Flitsha야’라고 해요. ‘너희 사람들이 우리에게 적들처럼 그렇게 했다고 말했고, 그들은 우리 사이에 불을 붙이고 fitna를 만들려고 했어’라고 하며 사과·잘못·행위자 방향·적대 행위·fitna 절을 보존해요.",
    },
    1139: {
        "english": "The speaker denies that anyone lit a fire of fitna between them: ‘They did not ignite any fire between us, nothing; I am telling you this.’ They say, ‘We are 3mwmia, we are nswbia, good people. Father, we are first cousins, we ourselves are children of the uncle.’ The negation, good-people claim, and kinship surfaces are retained.",
        "korean": "화자는 ‘그들이 우리 사이에 fitna의 불을 붙인 것이 아니야, 아무것도 아니야. 내가 너에게 말하는 거야’라고 부인해요. 이어 ‘우리는 3mwmia이고 nswbia이며 좋은 사람들이야. 아버지, 우리는 사촌이고 우리 스스로 삼촌의 자녀야’라고 하며 부정·좋은 사람이라는 주장·친족 표면을 모두 보존해요.",
    },
    1140: {
        "english": "The speaker says, ‘You—be quiet or swallow it; when elders speak, children fall silent.’ They retain the French-derived si di 9ws, si di zwnfwn, ail saf ba sw ki diz surface as an opaque children/kids turn. They say, ‘But the one who did this to us—you see him today; we will eat his flesh. He will pay dearly.’ Then: ‘Go, follow me, and leave it or mind your own business.’ The elders/young, threat, pay-dearly, follow-me, and khatik turns are all retained.",
        "korean": "화자는 ‘너, 입 다물어. 어른들이 말할 때 아이들은 조용히 해’라고 해요. 프랑스어 유래 si di 9ws, si di zwnfwn, ail saf ba sw ki diz 표면은 아이들에 관한 불투명한 turn으로 보존해요. 이어 ‘하지만 우리에게 이 일을 한 사람을 너는 오늘 보고 있지. 우리는 그의 살을 먹을 거야. 그는 비싸게 대가를 치를 거야’라고 위협해요. 마지막으로 ‘가서 나를 따라와. 그리고 내버려 둬, 네 일이나 신경 써’라고 하며 어른·아이·위협·대가·따라오라는 말·khatik turn을 모두 보존해요.",
    },
    1142: {
        "english": "The speaker says, ‘My brother, I—come kidnap me, or kidnap this person.’ They add, ‘Look how he is pretending to be helpless.’ The imperative and the shwf ki rah itmskn observation are both retained.",
        "korean": "화자는 ‘형제야, 나를 봐. 와서 나를 납치해, 아니면 이 사람을 납치해’라고 명령해요. 이어 ‘저 사람이 어떻게 불쌍한 척하는지 봐’라고 하며 명령형과 shwf ki rah itmskn 관찰 절을 모두 보존해요.",
    },
    1143: {
        "english": "The speaker begins, ‘I am telling you all, forgive me. Hazim, I want to ask you something: I want to become Indian like you.’ They say they do not hear an opaque Ania surface, then ask, ‘Listen to me: were you alone or with a group?’ and tell the other person to speak. They preserve ‘There were some with me; some with you.’ The speaker repeats, ‘I want to become Indian like you, forgive me,’ then says an opaque ‘do not become Indian; we are like you’ turn. They call Akasha and say, ‘Come, speak.’ They say God brought him and ask the listener to remember the day the listener took them; the listener asks, ‘Where did I take you?’ The speaker says, ‘You and your friend tied me and brought me here to Madam whom you remember.’ After ‘Fine, I remembered,’ they threaten, ‘Do you know what we will do to you? A tagine; today we will roast you and light the fire on you.’ Every question, identity turn, actor, restraint clause, Madam reference, and threat is retained.",
        "korean": "화자는 ‘너희에게 말하니 용서해 줘. Hazim, 너에게 물어볼 게 있어. 너처럼 인도인이 되고 싶어’라고 시작해요. 불투명한 Ania 표면을 들을 수 없다고 한 뒤 ‘내 말을 들어. 너는 혼자였어, 아니면 집단과 함께였어?’라고 묻고 상대에게 말하라고 해요. ‘나와 함께 몇몇이 있었고, 너와 함께 몇몇이 있었다’는 w7din 표현을 수량화하지 않고 보존해요. ‘너처럼 인도인이 되고 싶어, 용서해 줘’라고 반복하고 ‘인도인이 되지 마, 우리는 너희와 같아’라는 불투명한 turn을 남겨요. Akasha를 부르며 ‘어서 와서 말해’라고 하고, 하느님이 그를 데려왔다고 하며 상대에게 자신을 데려간 날을 기억하느냐고 물어요. 상대는 ‘내가 너를 어디로 데려갔지?’라고 되묻고, 화자는 ‘너와 네 친구가 나를 묶어 네가 기억하는 Madam에게 여기로 데려왔어’라고 해요. ‘그래, 기억났어’ 뒤에 ‘우리가 너에게 무엇을 할지 알아? 타진을 할 거야. 오늘 너를 굽고 네 위에 불을 붙일 거야’라고 위협해요. 모든 질문·정체성 turn·행위자·구속 절·Madam 지시·위협을 보존해요.",
    },
    1145: {
        "english": "The speaker says, ‘I am only a woman; release me. I did nothing. Why do you want to kill me? What did I do to you, my father, my brother?’ The plea for release, denial of wrongdoing, killing question, and bwia father/brother vocative are retained.",
        "korean": "화자는 ‘나는 그저 여자야. 나를 풀어 줘. 나는 아무것도 하지 않았어. 왜 나를 죽이려 해? 내가 너희에게 무슨 짓을 했어, 아버지 같은 분, 형제여?’라고 해요. 석방 요청·잘못 부인·살해 질문과 bwia의 아버지·형제 호격을 모두 보존해요.",
    },
    1146: {
        "english": "Mr Hazim is addressed: ‘Mr Hazim, I want to ask you: did you know the spy who was making trouble?’ The answer is, ‘Yes, I knew him, but I will leave it as a surprise—une surprise.’ The speaker then addresses a father/donkey/brother surface and says, ‘Do not move or budge. By God, I will give you every day a bidon of water and a kilo of grain.’ They repeat, ‘Oh donkey, my brother, do not budge.’ The spy question, answer, surprise, vocatives, water-and-grain promise, and repeated command are retained.",
        "korean": "화자는 Hazim 씨에게 ‘Hazim 씨, 물어보고 싶어. 문제를 일으키던 스파이를 알고 있었어?’라고 해요. 대답은 ‘응, 알고 있었어. 하지만 그건 놀라운 일, une surprise로 남겨 둘 거야’예요. 이어 아버지·당나귀·형제 표면으로 상대를 부르며 ‘움직이거나 꼼짝하지 마. 하느님께 맹세코 매일 물 한 통과 곡식 1킬로를 줄게’라고 해요. 마지막으로 ‘오, 당나귀 같은 형제야, 꼼짝하지 마’라고 반복하며 스파이 질문·응답·놀라움·호칭·물과 곡식 약속·반복 명령을 보존해요.",
    },
    1147: {
        "english": "The speaker says, ‘Hey donkey, you eat bran. I will buy you 9wfrit. Come on, go, donkey.’ The donkey-eats-bran clause, the opaque 9wfrit purchase, and the imperative mshi 7mar are all retained.",
        "korean": "화자는 ‘이봐, 당나귀야, 너는 겨를 먹어. 내가 너에게 9wfrit를 사 줄게. 어서 가, 당나귀야’라고 해요. 당나귀가 겨를 먹는다는 절, 불투명한 9wfrit 구매와 mshi 7mar 명령형을 모두 보존해요.",
    },
}


def apply():
    engine.BASE_COMMIT = BASE_COMMIT
    engine.BATCH_ID = BATCH_ID
    engine.CORRECTION_ID = CORRECTION_ID
    engine.PROMPT_VERSION = PROMPT_VERSION
    engine.BATCH_OUT = BATCH_OUT
    engine.BATCH_QA_OUT = BATCH_QA_OUT
    engine.CORRECTION_QA_OUT = CORRECTION_QA_OUT
    engine.EVIDENCE_PATH = EVIDENCE_PATH
    engine.PROVENANCE_BEFORE = PROVENANCE_BEFORE
    engine.CORRECTIONS = CORRECTIONS
    result = engine.apply()

    status = json.loads(engine.STATUS_OUT.read_text(encoding="utf-8"))
    status["counts"]["enrichment_draft_rows"] = 20
    status["counts"]["enrichment_flagged_rows"] = 802
    status["enrichment_correction_id"] = CORRECTION_ID
    engine.STATUS_OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(BATCH_QA_OUT.read_text(encoding="utf-8"))
    qa["draft_rows"] = 20
    qa["flagged_rows"] = 44
    qa["correction_state_updates"] = 0
    qa["correction_history"][-1]["state_updates"] = 0
    BATCH_QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    correction = json.loads(CORRECTION_QA_OUT.read_text(encoding="utf-8"))
    correction["state_updates"] = 0
    correction["batch_artifact_sync_state_updates"] = 0
    correction["draft_rows"] = 20
    correction["flagged_rows"] = 44
    CORRECTION_QA_OUT.write_text(json.dumps(correction, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result.update({"state_updates": 0, "draft_rows": 20, "flagged_rows": 44})
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(apply(), ensure_ascii=False, indent=2))
