"""Build the text-prosody report from documented study outputs; never fit a model."""
from pathlib import Path
from html import escape
import json
import shutil

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/Text-Prosody-Misalignment.pdf'
FIGS = ROOT / 'paper/prosody-figures'
FIGS.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
for name in ['figure1_conceptual_va_space.png', 'figure2_roc_comparison.png', 'ads_sentiment_box_violin.png']:
    if not (FIGS / name).is_file():
        raise FileNotFoundError(FIGS / name)

for name, file in [('Body','georgia.ttf'),('Body-Bold','georgiab.ttf'),('Body-Italic','georgiai.ttf'),('Body-BoldItalic','georgiaz.ttf'),('Sans','calibri.ttf'),('Sans-Bold','calibrib.ttf'),('Sans-Italic','calibrii.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Body-Bold', italic='Body-Italic', boldItalic='Body-BoldItalic')
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-Bold', italic='Sans-Italic', boldItalic='Sans-Italic')
INK=colors.HexColor('#202b2b'); GREEN=colors.HexColor('#224d47'); MUTED=colors.HexColor('#54645f'); LINE=colors.HexColor('#ccd6d0')
styles={
    'body':ParagraphStyle('body',fontName='Body',fontSize=10.2,leading=14.2,textColor=INK,spaceAfter=8),
    'title':ParagraphStyle('title',fontName='Body-Bold',fontSize=23,leading=28,textColor=GREEN,spaceAfter=13),
    'subtitle':ParagraphStyle('subtitle',fontName='Sans',fontSize=13,leading=18,textColor=MUTED,spaceAfter=14),
    'author':ParagraphStyle('author',fontName='Sans',fontSize=10.5,leading=15,textColor=INK,spaceAfter=17),
    'h1':ParagraphStyle('h1',fontName='Sans-Bold',fontSize=17,leading=21,textColor=GREEN,spaceAfter=13,keepWithNext=True),
    'h2':ParagraphStyle('h2',fontName='Sans-Bold',fontSize=12.2,leading=16,textColor=GREEN,spaceBefore=9,spaceAfter=7,keepWithNext=True),
    'caption':ParagraphStyle('caption',fontName='Sans',fontSize=9,leading=12.5,textColor=MUTED,spaceAfter=13),
    'cell':ParagraphStyle('cell',fontName='Sans',fontSize=9,leading=12,textColor=INK),
    'cellhead':ParagraphStyle('cellhead',fontName='Sans-Bold',fontSize=9,leading=12,textColor=GREEN),
    'ref':ParagraphStyle('ref',fontName='Body',fontSize=9.1,leading=13.2,leftIndent=15,firstLineIndent=-15,spaceAfter=11,textColor=INK),
    'equation':ParagraphStyle('equation',fontName='Body',fontSize=11,leading=17,textColor=INK,alignment=TA_CENTER,spaceBefore=7,spaceAfter=13),
}
story=[]
def p(s,style='body'): story.append(Paragraph(s,styles[style]))
def h(s): p(s,'h1')
def sub(s): p(s,'h2')
def page(): story.append(PageBreak())
def table(caption, rows, widths, highlight=None):
    p(caption,'caption')
    cells=[[Paragraph(x,styles['cellhead' if i==0 else 'cell']) for x in row] for i,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    commands=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eee9')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,LINE),('LINEBELOW',(0,1),(-1,-1),.35,LINE),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]
    if highlight is not None:commands.append(('BACKGROUND',(0,highlight),(-1,highlight),colors.HexColor('#f1f5ef')))
    t.setStyle(TableStyle(commands));story.extend([t,Spacer(1,12)])
def fig(name,caption,maxw=440,maxh=330):
    image_path=FIGS/name
    with PILImage.open(image_path) as im:w,ht=im.size
    scale=min(maxw/w,maxh/ht)
    image=Image(str(image_path),w*scale,ht*scale)
    image.hAlign='CENTER'
    story.append(KeepTogether([image,Spacer(1,8),Paragraph(caption,styles['caption'])]))

p('Text-Prosody Misalignment<br/>and PHQ-8 Scores','title')
p('An Exploratory Multimodal Study','subtitle')
p('Robert J. Leggieri<br/>The University of Texas at Austin','author')
sub('Abstract')
p('This study investigates whether an explicit comparison of text-derived and audio-derived affect features is associated with PHQ-8 symptom scores. I designed the Alignment Discrepancy Score (ADS) and implemented a pipeline spanning transcript preparation, timestamped audio segmentation, pretrained-model inference, session-level feature engineering, and predictive evaluation. The completed feature pipeline covers 32,401 utterances from 189 DAIC-WOZ interviews. Sentiment-based ADS was the stronger of the two implemented text representations: the feature-set experiment recorded mean AUC 0.619, compared with 0.501 for emotion-based ADS. A separate five-fold, out-of-fold sentiment-ADS analysis produced AUC 0.609 (95% bootstrap interval 0.522-0.693) and average precision 0.410 (0.309-0.540), above the 0.302 prevalence baseline. In the saved ROC comparison, text-only features achieved AUC 0.706, exceeding sentiment-ADS. A verified label-adapter defect reduces the implemented audio projection to a transformation of sadness-class probability. The predictive results therefore describe the implemented features; they do not establish that ADS measures psychological incongruence. The study contributes a working multimodal research pipeline, a measurable representation-dependent association with PHQ group, and a concrete account of the measurement and evaluation changes needed to test the intended construct.')
p('<b>Keywords:</b> multimodal learning; affective computing; text and speech; PHQ-8; feature engineering; model evaluation.','caption')
sub('Research questions')
p('<b>1.</b> Can utterance-level text/audio outputs be turned into an explicit, inspectable discrepancy feature?<br/><b>2.</b> How do emotion-based and sentiment-based versions behave in session-level PHQ prediction?<br/><b>3.</b> What do predictive performance, baseline comparisons, and implementation checks establish about that feature?')

page();h('1. Motivation and related work')
p('Language and delivery offer different descriptions of an interview. A transcript preserves lexical content; the audio carries timing, pitch, energy, and other vocal characteristics. The research question is whether an explicit relationship between the two streams provides a useful feature for studying symptom-associated behavior. This question motivates ADS without assuming that a mismatch reveals a person\'s internal emotional state.')
sub('Speech, symptoms, and the value of multimodal analysis')
p('Yang et al. (2013) studied vocal prosody in relation to changes in depression severity, and Cummins et al. (2015) reviewed speech-based depression and suicide-risk research. These works support investigating acoustic information while emphasizing the importance of recording conditions, sample composition, and generalization. They do not establish that any single acoustic or cross-modal feature is specific to depression.')
p('Multimodal learning includes representation, alignment, and fusion problems (Baltrusaitis et al., 2019). ADS makes one relationship explicit: the distance between coordinates derived from text and speech models. That choice makes the calculation easy to inspect and permits simple downstream models. Mathematical transparency alone does not guarantee that the coordinates share a valid psychological scale.')
sub('Affect representations and their limits')
p('Russell\'s (1980) circumplex model provides a conceptual basis for describing affect along valence and arousal dimensions. Fontaine et al. (2007), however, found that additional dimensions were needed to represent the meaning of emotion words adequately. These sources motivate a low-dimensional approximation and its limitations. They do not supply the exact numerical anchors used by this implementation, nor do they calibrate the outputs of separately trained classifiers onto a common scale.')
p('Cross-modal disagreement also occurs outside mental-health settings. MUStARD, introduced by Castro et al. (2019), illustrates the relevance of verbal and nonverbal cues to sarcasm. This establishes an alternative context for discrepant cues, not evidence that high ADS identifies sarcasm or emotional masking in DAIC-WOZ. Context, conversational function, model error, and the choice of affect representation can all produce apparent disagreement.')
sub('Study contribution')
p('The contribution is an implemented research approach: align participant utterances across modalities, define two text/audio discrepancy variants, summarize their behavior over a session, and assess the resulting features against PHQ outcomes. The study reports positive predictive findings and an important implementation failure together. That combination identifies what the pipeline achieved and what must change before the intended measure can be validated.')

page();h('2. Data and end-to-end implementation')
sub('Corpus and prediction target')
p('The analysis uses 189 labeled DAIC-WOZ sessions. DAIC was developed for studying psychological distress through human and computer interviews (Gratch et al., 2014); the related SimSensei work describes a virtual-interviewer research platform (DeVault et al., 2014). This study uses audio and timestamped transcripts, rather than video or the corpus\'s supplied COVAREP features.')
p('The binary target is PHQ-8 &gt;= 10. There are 57 elevated-score sessions and 132 below-threshold sessions, giving a positive-class prevalence of 57/189 = 0.3016. PHQ-8 is a symptom questionnaire with established research use (Kroenke et al., 2009). Here, the labels identify questionnaire-score groups, not independently adjudicated diagnoses. Ridge regression also targets the continuous PHQ-8 score.')
p('The working cohort combines sessions from official DAIC-WOZ partitions. The reported cross-validation therefore describes this pooled research cohort. It is not an untouched official-test evaluation or a directly comparable challenge submission.')
sub('Preparation, alignment, and feature extraction')
p('<b>Session preparation.</b> I built manifests, joined PHQ labels, extracted participant-only transcript turns, and used their timestamps to create utterance-level audio clips. Excluding interviewer turns reduces direct reliance on prompts. Burdisso et al. (2024) demonstrate why interviewer content can create shortcuts in DAIC-WOZ; participant responses can still reflect the topics and structure of the interview.')
p('<b>Classical audio features.</b> I extracted 13 MFCC coefficients with mean and standard-deviation summaries, fundamental-frequency statistics using YIN, RMS energy, zero-crossing rate, and duration with librosa. Audio is processed at 16 kHz in mono. These descriptors provide inspectable acoustic features alongside the pretrained affect outputs.')
p('<b>Pretrained text and audio inference.</b> Separate stages generate text embeddings, categorical text-emotion predictions, sentiment probabilities, and speech-emotion probabilities. The audio stage supports batched inference, checkpointing, resumption, and model-status logging. The ADS calculations use the available SUPERB audio projection and two text projections; the requested second audio-model branch did not produce columns used in the ADS rollups.')
p('<b>Coverage and operational checks.</b> The ADS quality-control summary records 32,401 utterances, 32,401 audio rows, 32,401 text rows, and 189 session rollups, with no missing required rows for the two completed ADS pairings. The classical audio log records 15 short-window warnings while retaining feature rows for all utterances. Complete coverage establishes successful processing, not correctness of each prediction or projection.')

page();h('3. Affect representations and the audio adapter')
sub('Text representations')
p('The emotion variant uses <i>j-hartmann/emotion-english-distilroberta-base</i> (Hartmann, 2022), a seven-class English emotion classifier. For each utterance, its class probabilities are converted to coordinates by a probability-weighted average of fixed anchors. The implemented text anchors are shown in Table 1.')
table('<b>Table 1.</b> Heuristic anchors used by the text-emotion projection.',[
 ['Emotion','Valence anchor','Arousal anchor'],['Anger','-0.7','0.8'],['Disgust','-0.6','0.2'],['Fear','-0.7','0.9'],['Joy','0.8','0.6'],['Neutral','0.0','0.1'],['Sadness','-0.8','0.2'],['Surprise','0.2','0.8']], [210,120,138])
p('The sentiment variant uses <i>cardiffnlp/twitter-roberta-base-sentiment-latest</i> (Cardiff NLP, 2022), an English sentiment model trained outside this interview setting. From its positive, negative, and neutral probabilities, the implementation defines:')
p('V<sub>text</sub> = p<sub>positive</sub> - p<sub>negative</sub><br/>A<sub>text</sub> = 1 - p<sub>neutral</sub>','equation')
p('The second coordinate is a non-neutrality proxy. Calling it arousal does not make it a validated arousal estimate. Both text variants produce model-derived coordinates whose meaning depends on these transformations.')
sub('What the audio adapter actually computes')
p('The audio checkpoint is <i>superb/wav2vec2-base-superb-er</i>, a speech-emotion classifier associated with the SUPERB benchmark (SUPERB, 2021). Its configuration returns the labels <i>neu</i>, <i>hap</i>, <i>ang</i>, and <i>sad</i>. The adapter recognizes <i>sad</i>, but its lookup dictionary expects full words for the other three classes. Unknown labels contribute zero to both coordinates. With normalized probabilities, the implemented projection consequently reduces to:')
p('V<sub>audio</sub> = -0.8 p<sub>sad</sub> &nbsp;&nbsp;&nbsp; A<sub>audio</sub> = 0.2 p<sub>sad</sub>','equation')
p('This adapter defect is visible in all 32,401 saved audio-coordinate pairs: V<sub>audio</sub> + 4A<sub>audio</sub> = 0 exactly. The predictive results describe this implementation, rather than a validated two-dimensional text-prosody discrepancy measure.')

page();h('4. ADS construction and session features')
p('For utterance i, ADS is the Euclidean distance between the text and audio coordinates:')
p('ADS<sub>i</sub> = [(V<sub>text,i</sub> - V<sub>audio,i</sub>)<super>2</super> + (A<sub>text,i</sub> - A<sub>audio,i</sub>)<super>2</super>]<super>1/2</super>','equation')
p('I implemented separate emotion-ADS and sentiment-ADS pairings. Figure 1 illustrates the intended geometry. Small distances mean the chosen coordinates are close; large distances mean they are far apart under the selected mappings. Neither statement establishes that a participant was emotionally congruent, concealing distress, or experiencing a particular emotion.')
fig('figure1_conceptual_va_space.png','<b>Figure 1.</b> ADS geometry in a valence-arousal coordinate system. The points and arrows are conceptual examples created for this study, not participant observations. The illustration explains the distance calculation; the implemented audio coordinates have the one-dimensional constraint described in Section 3.',maxw=390,maxh=305)
p('Five features summarize each session: <b>mean</b>, <b>standard deviation</b>, <b>maximum</b>, <b>proportion above 0.6</b>, and <b>longest consecutive run above 0.6</b>. The code uses standard deviation, not variance. These features retain differences in average magnitude, spread, extremes, frequency, and persistence. The 0.6 cutoff is a feature-engineering choice, not a clinical threshold.')
p('The run-length feature counts successive retained utterances in their processed order; it is not duration in seconds. A high-ADS run can therefore reflect turn segmentation as well as sustained model-output discrepancy. This distinction matters when interpreting temporal features or comparing interviews with different utterance lengths.')

page();h('5. Predictive evaluation')
sub('Models and units of analysis')
p('The predictive unit is the session, not the utterance. Logistic-regression pipelines standardize the input features and use class-balanced fitting for PHQ-group classification. Ridge regression predicts PHQ-8 scores. Feature extraction uses pretrained checkpoints; the study does not fine-tune them on PHQ labels.')
p('The analyses have distinct outputs and protocols. Keeping them separate prevents a fold-average number from being treated as the same estimate as an AUC calculated over pooled out-of-fold predictions.')
table('<b>Table 2.</b> Analysis outputs and interpretation.',[
 ['Analysis','Available output','Interpretation'],
 ['ADS feature-set experiment','Fold summaries for three ADS feature sets','Descriptive variant comparison; incomplete run metadata.'],
 ['Sentiment-ADS operating-point analysis','189 predictions, five fold IDs, metrics and intervals','Stratified five-fold session-level evaluation.'],
 ['ROC baseline comparison','Saved curves and model-fitting plot script','Separate five-fold baseline comparison.']], [112,170,186])
sub('Cross-validation and model selection')
p('The operating-point script uses five stratified folds, shuffling with random seed 42. The saved record contains one prediction for each of 189 unique session identifiers, with fold sizes 38, 38, 38, 38, and 37. Scaling is fitted within each training fold. No utterance-level prediction is randomly split across training and evaluation in this analysis.')
p('The broader modeling script supports five-fold GroupKFold when participant identifiers are present and a shuffled ten-fold KFold fallback otherwise. It also contains training-set threshold tuning and fusion-model exploration. Those code paths do not justify describing all experiments as leave-one-participant-out validation or as one uniformly stratified protocol. The exact configuration behind the feature-set summary in Table 5 is not fully recoverable from the retained run record.')
sub('Metrics, intervals, and threshold selection')
p('The operating-point analysis records ROC AUC, average precision (reported as AUPRC), Brier score, and sensitivity/specificity with predictive values. Its 95% percentile-bootstrap intervals use 1,000 resamples of the fixed out-of-fold label/probability pairs. They quantify variability within that prediction record, not uncertainty from repeating model selection, feature development, or dataset collection.')
p('The Youden and sensitivity-oriented thresholds are selected using the pooled out-of-fold labels and scores, then summarized on those same scores. Their operating characteristics describe an explored trade-off. They are not independently evaluated thresholds ready for deployment.')

page();h('6. Results: inspectable out-of-fold predictions')
sub('Sentiment-ADS ranks PHQ groups above chance')
p('The sentiment-ADS classifier produced <b>AUC 0.609</b> and <b>average precision 0.410</b> across 189 out-of-fold predictions. Average precision exceeds the positive-class prevalence of <b>0.302</b> by 0.108. Both saved bootstrap intervals have lower endpoints above their corresponding chance or prevalence reference. These are positive predictive results for the implemented features in this cohort.')
table('<b>Table 3.</b> Sentiment-ADS out-of-fold performance.',[
 ['Metric','Estimate','95% bootstrap interval'],['ROC AUC','0.609','0.522-0.693'],['Average precision (AUPRC)','0.410','0.309-0.540'],['Positive-class prevalence','0.302','Reference level'],['Brier score','0.238','Not recorded']], [230,85,153])
p('Discrimination and probability quality give different answers. A constant predictor equal to the full-cohort prevalence has Brier score p(1-p) = 0.211 on these labels, lower than the model\'s 0.238. This descriptive reference shows that the model\'s ranking advantage does not translate into improved squared-error probability prediction. It does not support a claim of good calibration or an improvement from calibration tuning.')
sub('Operating points make the cost visible')
table('<b>Table 4.</b> Explored thresholds on the pooled out-of-fold predictions.',[
 ['Quantity','Youden threshold','Sensitivity-oriented threshold'],['Probability cutoff','0.457','0.395'],['Sensitivity','73.7%','80.7%'],['Specificity','50.8%','31.8%'],['Positive predictive value','39.3%','33.8%'],['Negative predictive value','81.7%','79.2%'],['True positives / false negatives','42 / 15','46 / 11'],['True negatives / false positives','67 / 65','42 / 90']], [230,112,126])
p('Lowering the threshold identifies four additional elevated-score sessions and adds 25 false positives. At the sensitivity-oriented cutoff, 90 of 132 below-threshold sessions are flagged. Reporting that cost alongside sensitivity gives a concrete account of performance. The experiment does not establish a favorable clinical-triage trade-off.')

page();h('7. Representation and baseline comparisons')
sub('Sentiment-based ADS was the stronger variant')
table('<b>Table 5.</b> ADS feature-set experiment: recorded fold means +/- standard deviations.',[
 ['Feature set','F1','AUC','PHQ-8 RMSE'],['Emotion-ADS','0.429 +/- 0.140','0.501 +/- 0.178','5.93 +/- 0.76'],['Sentiment-ADS','0.464 +/- 0.168','0.619 +/- 0.133','5.57 +/- 0.96'],['Combined ADS','0.425 +/- 0.181','0.578 +/- 0.167','5.68 +/- 0.90']], [132,112,112,112],highlight=2)
p('Sentiment-ADS has the highest recorded AUC and F1 and the lowest recorded RMSE among these three feature sets. The direction is useful: changing the text representation changes the behavior of the implemented discrepancy feature. The fold standard deviations are substantial, and the table supplies no paired uncertainty interval for the difference between variants. The values are descriptive summaries, not a statistical demonstration of superiority.')
sub('Text-only prediction remained stronger')
fig('figure2_roc_comparison.png','<b>Figure 2.</b> ROC comparison: text-only AUC 0.706, sentiment-ADS 0.609, audio-only 0.486, and emotion-ADS 0.461. Text-only is the strongest classifier shown. This comparison is separate from the fold summaries in Table 5.',maxw=300,maxh=260)
p('For this comparison, text-only and audio-only inputs are session-level means and standard deviations of affect coordinates. The extracted text embeddings and classical acoustic descriptors are separate pipeline outputs, not the baselines displayed here. Sentiment-ADS exceeds the audio-affect baseline in this plot but does not beat text-only. These outputs do not demonstrate incremental value from adding ADS to text features.')

page();h('8. Distributional observations')
fig('ads_sentiment_box_violin.png','<b>Figure 3.</b> Session-mean sentiment-ADS by PHQ group. The groups have similar medians, while the PHQ-elevated group has a narrower central spread. The dashed line marks the global mean plus one standard deviation. The plot\'s group labels denote the PHQ-8 cutoff, not independently confirmed diagnoses.',maxw=370,maxh=280)
p('The session-mean distributions overlap substantially. The below-threshold group has a broader central range; the PHQ-elevated group is more concentrated around a similar median. Outlying values occur in both groups. This is a descriptive observation about the implemented score, not evidence of a general law about emotional variability in depression.')
p('The result directs attention toward spread and temporal structure rather than a simple shift in average discrepancy. The pipeline already provides standard deviation, high-score proportion, and run-length features for that purpose. However, the experiment does not isolate their individual contributions through held-out ablations. A difference in the spread of session means also does not establish reduced within-person emotional variability.')
sub('What a high-score segment can show')
p('Ranking utterances by ADS provides an inspection mechanism: a researcher can examine the source text, listen to the aligned audio, and check the intermediate model outputs. It is useful for debugging alignment, probing the score, and designing annotation. Selection by ADS itself cannot verify that an utterance contains genuine incongruence.')
p('The study has no blinded paired-modality reference labels or independent masking annotations. Selected examples and the distribution plot therefore cannot establish concealed distress or flattened affect. The observed association concerns an engineered score whose psychological interpretation remains to be tested.')

page();h('9. Discussion')
sub('A completed implementation with a measurable outcome')
p('The study moves beyond a conceptual proposal. I implemented the chain from timestamped interview records to model-ready session features, handled two different text representations, processed 32,401 utterances, and produced classification, regression, distributional, and threshold analyses. Coverage and warning logs make major processing conditions inspectable. These are concrete research-software contributions even though the intended measurement construct remains unvalidated.')
p('The numerical evidence also contains a positive result. In the inspectable five-fold prediction record, sentiment-ADS ranks elevated-PHQ sessions above below-threshold sessions better than chance and yields average precision above prevalence. The effect is modest, but it is measurable in the retained predictions. It warrants a controlled follow-up rather than either a biomarker claim or dismissal of the entire approach.')
sub('What the representation comparison means')
p('The strongest empirical direction is representation dependence. Sentiment-based ADS performs better than emotion-based ADS in the feature-set summaries and in the ROC comparison, although the exact estimates differ across those analyses. This identifies a practical modeling choice worth testing: a compact sentiment representation was more useful than the chosen text-emotion projection in this implementation.')
p('That result cannot establish that dimensional representations generally outperform categorical emotion models. Both variants begin with categorical predictions, use different model training data and class sets, and apply different coordinate transformations. The adapter error also changes the intended audio representation. An apparent advantage can arise from any combination of those factors.')
sub('Prediction, measurement, and complementary information')
p('ADS is transparent as an arithmetic operation. Its coordinates and distance can be inspected, and the session features have clear computational definitions. Psychological interpretation requires another kind of evidence: agreement with independent judgments about the affect expressed in each modality, together with evidence that the two coordinates are comparable. A useful PHQ predictor can exist without satisfying those measurement requirements.')
p('The text-only baseline makes the next question precise. Since text-only AUC is 0.706 in the saved comparison, the current outputs do not establish that ADS adds information beyond language alone. A paired outer-fold comparison of text versus text-plus-ADS is needed. Raw text/audio coordinates should also be tested, because the Euclidean distance may simply repackage a strong unimodal signal. Demonstrating an interpretable interaction requires showing what the comparison adds beyond its components.')

page();h('10. Limits and a focused follow-up design')
sub('Repair and validate the measurement layer first')
p('The first task is explicit label normalization with tests for all four SUPERB outputs. Unknown labels should raise an error rather than silently map to zero. The existing performance values must remain attached to the implementation that generated them. Correcting the adapter changes the features and requires a new analysis; it cannot be described as a cosmetic correction.')
p('Next, collect paired reference judgments for text and audio affect using a documented annotation protocol. Examine annotator agreement, reliability, range, and scaling for each dimension. Fit any calibration or normalization only within training data. Test whether cross-modal distance changes materially under reasonable coordinate mappings. The non-neutrality proxy should be evaluated as its own construct, rather than assumed to measure arousal.')
sub('Separate development, selection, and final evaluation')
p('The pooled DAIC-WOZ cohort has already been used for feature exploration and comparison, including sessions from official partitions. It cannot provide a fresh final test of the revised method. A new held-out cohort or another appropriately licensed dataset is needed for an independent estimate. Within development data, all feature choices, hyperparameters, calibration, fusion weights, and probability thresholds should be selected inside inner participant-grouped folds.')
p('Outer folds should produce one immutable prediction record per comparison. Figures should read that record without fitting another model. Report paired differences with participant-level uncertainty, and keep the cohort, labels, feature definitions, and folds identical across text, audio, ADS, and fusion models. This directly addresses the differing summary and plotting protocols in the current study.')
sub('Run ablations that answer the actual research question')
p('The essential comparison is text alone versus text plus ADS, alongside audio alone and concatenated text/audio coordinates. Additional ablations should separate valence and the arousal proxy, remove individual session statistics, vary the high-score cutoff, and control for utterance count and duration. These tests can reveal whether a benefit comes from cross-modal structure, a single component, or segmentation and recording artifacts.')
p('Report discrimination, calibration, and operating-point costs separately. The present Brier result makes probability evaluation especially important. Fixed-threshold performance should be measured on data unused for choosing that threshold. Larger and more diverse samples are also needed to evaluate demographic, linguistic, recording-condition, and interview-context variation; the present study contains no established fairness or transportability result.')

page();h('11. Responsible interpretation and conclusion')
sub('Data handling and use')
p('Interview recordings and transcripts contain sensitive information. Access, storage, processing, and sharing must follow the DAIC-WOZ agreement and applicable research requirements. Reproducible code and aggregate outputs can document an experiment without publishing participant recordings, transcript excerpts, or linked identifiers. This report uses conceptual and aggregate figures rather than identifiable examples.')
p('PHQ-group prediction should not be presented as a judgment about a person\'s honesty, hidden feelings, or willingness to disclose distress. A high score is a consequence of model outputs and mapping rules. It is not evidence of deception or emotional masking. The threshold results also show a substantial false-positive burden, so this study provides no basis for clinical screening, triage, or treatment decisions.')
sub('Conclusion')
p('This study implemented ADS as an explicit text/audio feature and completed an end-to-end analysis of 189 DAIC-WOZ interviews and 32,401 utterances. Sentiment-based ADS was the stronger implemented variant, and the saved five-fold predictions produced AUC 0.609 and average precision 0.410 against prevalence 0.302. Those findings identify a modest, measurable predictive association in the studied cohort.')
p('The baseline comparison and implementation checks define the result\'s limits. Text-only prediction was stronger in the ROC comparison; the recorded probability estimates did not improve on a prevalence-only Brier reference; and the audio-label adapter collapsed the intended speech-affect projection. Consequently, the experiment establishes performance of an engineered feature pipeline, not a validated measure of psychological incongruence or a depression biomarker.')
p('The next study has a concrete path: correct and test the adapter, establish comparable modality-specific measurements, compare text with text-plus-ADS under nested grouped evaluation, and assess the frozen method on new data. The work contributes both a functioning research pipeline and an empirical basis for deciding which parts of the proposed measure deserve further investigation.')

page();h('References')
refs=[
('Baltrusaitis, T., Ahuja, C., &amp; Morency, L.-P. (2019).','Multimodal machine learning: A survey and taxonomy. <i>IEEE Transactions on Pattern Analysis and Machine Intelligence, 41</i>(2), 423-443.','https://doi.org/10.1109/TPAMI.2018.2798607'),
('Burdisso, S., Reyes-Ramirez, E., Villatoro-Tello, E., Sanchez-Vega, F., Lopez-Monroy, A. P., &amp; Motlicek, P. (2024).',"DAIC-WOZ: On the validity of using the therapist's prompts in automatic depression detection from clinical interviews. In <i>Proceedings of the 6th Clinical Natural Language Processing Workshop</i> (pp. 82-90).",'https://aclanthology.org/2024.clinicalnlp-1.8/'),
('Cardiff NLP. (2022).','<i>Twitter-roBERTa-base for sentiment analysis - updated (2022)</i> [Model card].','https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest'),
('Castro, S., Hazarika, D., Perez-Rosas, V., Zimmermann, R., Mihalcea, R., &amp; Poria, S. (2019).','Towards multimodal sarcasm detection (an obviously perfect paper). In <i>Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics</i> (pp. 4619-4629).','https://aclanthology.org/P19-1455/'),
('Cummins, N., Scherer, S., Krajewski, J., Schnieder, S., Epps, J., &amp; Quatieri, T. F. (2015).','A review of depression and suicide risk assessment using speech analysis. <i>Speech Communication, 71</i>, 10-49.','https://doi.org/10.1016/j.specom.2015.03.004'),
('DeVault, D., Artstein, R., Benn, G., Dey, T., Fast, E., Gainer, A., Georgila, K., Gratch, J., Hartholt, A., Lhommet, M., Lucas, G., Marsella, S., Morbini, F., Nazarian, A., Scherer, S., Stratou, G., Suri, A., Traum, D., Wood, R., Xu, Y., Rizzo, A., &amp; Morency, L.-P. (2014).','SimSensei kiosk: A virtual human interviewer for healthcare decision support. In <i>Proceedings of AAMAS 2014</i> (pp. 1061-1068).','https://nld.ict.usc.edu/cs644-spring2020/discussions/devault-etal-aamas2014.pdf'),
('Fontaine, J. R. J., Scherer, K. R., Roesch, E. B., &amp; Ellsworth, P. C. (2007).','The world of emotions is not two-dimensional. <i>Psychological Science, 18</i>(12), 1050-1057.','https://doi.org/10.1111/j.1467-9280.2007.02024.x'),
('Gratch, J., Artstein, R., Lucas, G., Stratou, G., Scherer, S., Nazarian, A., Wood, R., Boberg, J., DeVault, D., Marsella, S., Traum, D., Rizzo, S., &amp; Morency, L.-P. (2014).','The Distress Analysis Interview Corpus of human and computer interviews. In <i>Proceedings of LREC 2014</i> (pp. 3123-3128).','https://aclanthology.org/L14-1421/'),
('Hartmann, J. (2022).','<i>Emotion English DistilRoBERTa-base</i> [Model card].','https://huggingface.co/j-hartmann/emotion-english-distilroberta-base'),
('Kroenke, K., Strine, T. W., Spitzer, R. L., Williams, J. B. W., Berry, J. T., &amp; Mokdad, A. H. (2009).','The PHQ-8 as a measure of current depression in the general population. <i>Journal of Affective Disorders, 114</i>(1-3), 163-173.','https://doi.org/10.1016/j.jad.2008.06.026'),
('Russell, J. A. (1980).','A circumplex model of affect. <i>Journal of Personality and Social Psychology, 39</i>(6), 1161-1178.','https://doi.org/10.1037/h0077714'),
('SUPERB. (2021).','<i>Wav2Vec2-base for emotion recognition</i> [Model card and checkpoint configuration].','https://huggingface.co/superb/wav2vec2-base-superb-er'),
('Yang, Y., Fairbairn, C., &amp; Cohn, J. F. (2013).','Detecting depression severity from vocal prosody. <i>IEEE Transactions on Affective Computing, 4</i>(2), 142-150.','https://doi.org/10.1109/T-AFFC.2012.38'),
]
for author,title,url in refs:
    p(f'{author} {title} <link href="{escape(url,quote=True)}" color="#224d47">{escape(url)}</link>','ref')

def decorate(c,doc):
    c.saveState();w,ht=LETTER
    c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(72,ht-42,w-72,ht-42)
    c.setFillColor(MUTED);c.setFont('Sans',8)
    c.drawString(72,ht-33,'TEXT-PROSODY MISALIGNMENT AND PHQ-8 SCORES')
    c.drawString(72,35,'Robert J. Leggieri')
    c.drawRightString(w-72,35,str(doc.page));c.restoreState()
doc=SimpleDocTemplate(str(OUT),pagesize=LETTER,rightMargin=72,leftMargin=72,topMargin=60,bottomMargin=55,title='Text-Prosody Misalignment and PHQ-8 Scores: An Exploratory Multimodal Study',author='Robert J. Leggieri',subject='A multimodal research pipeline, observed PHQ-group associations, and measurement validity')
doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
for folder in ['docs', 'public/docs']:
    shutil.copyfile(OUT, ROOT / folder / OUT.name)
print(OUT)
