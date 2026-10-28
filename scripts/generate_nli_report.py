"""Build the standalone NLI research paper and synchronize its published copies."""
from pathlib import Path
from html import escape
import shutil

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import Font
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle,
)
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output/pdf/Making-DeBERTa-Smarter.pdf'
FIGURE = ROOT / 'paper/figures/original-mnli-data-map.png'

# Experimental results for the baseline and category-weighted models.
MNLI_METRICS = [
    ['Evaluation loss', '0.6366', '0.6101'],
    ['Evaluation accuracy', '0.8891', '0.8847'],
    ['Evaluation runtime (s)', '51.546', '48.340'],
    ['Samples per second', '190.412', '203.040'],
    ['Steps per second', '23.804', '25.383'],
]
MNLI_CLASSES = [
    ['Base', 'Contradiction', '0.935', '0.865', '0.899', '3479'],
    ['Base', 'Neutral', '0.821', '0.880', '0.849', '3123'],
    ['Base', 'Entailment', '0.914', '0.925', '0.919', '3213'],
    ['Base', 'Overall', '0.892', '0.889', '0.890', '9815'],
    ['Re-weighted', 'Contradiction', '0.932', '0.862', '0.896', '3479'],
    ['Re-weighted', 'Neutral', '0.818', '0.873', '0.845', '3123'],
    ['Re-weighted', 'Entailment', '0.906', '0.920', '0.913', '3213'],
    ['Re-weighted', 'Overall', '0.887', '0.885', '0.885', '9815'],
]
HANS = [
    ['Constituent','ce_adverb','100.00%','100.00%'],
    ['','ce_after_since_clause','100.00%','100.00%'],
    ['','ce_conjunction','100.00%','100.00%'],
    ['','ce_embedded_under_since','99.60%','99.00%'],
    ['','ce_embedded_under_verb','99.90%','99.90%'],
    ['','cn_adverb','61.90%','63.40%'],
    ['','cn_after_if_clause','0.00%','1.40%'],
    ['','cn_disjunction','0.40%','1.50%'],
    ['','cn_embedded_under_if','68.20%','67.40%'],
    ['','cn_embedded_under_verb','58.60%','68.50%'],
    ['Lexical overlap','le_around_prepositional_phrase','100.00%','99.90%'],
    ['','le_around_relative_clause','99.90%','99.90%'],
    ['','le_conjunction','99.40%','99.30%'],
    ['','le_passive','100.00%','100.00%'],
    ['','le_relative_clause','99.30%','98.80%'],
    ['','ln_conjunction','94.80%','97.70%'],
    ['','ln_passive','98.40%','99.00%'],
    ['','ln_preposition','96.30%','98.50%'],
    ['','ln_relative_clause','94.40%','96.90%'],
    ['','ln_subject/object_swap','99.80%','99.90%'],
    ['Subsequence','se_PP_on_obj','100.00%','100.00%'],
    ['','se_adjective','100.00%','100.00%'],
    ['','se_conjunction','100.00%','99.70%'],
    ['','se_relative_clause_on_obj','100.00%','100.00%'],
    ['','se_understood_object','100.00%','100.00%'],
    ['','sn_NP/S','0.10%','0.00%'],
    ['','sn_NP/Z','3.40%','4.00%'],
    ['','sn_PP_on_subject','66.30%','69.90%'],
    ['','sn_past_participle','2.90%','8.00%'],
    ['','sn_relative_clause_on_subject','81.10%','85.00%'],
    ['Overall accuracy','','77.49%','78.59%'],
]

REFERENCES = [
    ('Clark, K., Luong, M.-T., Le, Q. V., and Manning, C. D. (2020).',
     'ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators. ICLR.',
     'https://arxiv.org/abs/2003.10555'),
    ('Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. (2019).',
     'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT, 4171-4186.',
     'https://aclanthology.org/N19-1423/'),
    ('He, P., Liu, X., Gao, J., and Chen, W. (2021).',
     'DeBERTa: Decoding-enhanced BERT with Disentangled Attention. ICLR.',
     'https://arxiv.org/abs/2006.03654'),
    ('He, P., Gao, J., and Chen, W. (2023).',
     'DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding Sharing. ICLR.',
     'https://arxiv.org/abs/2111.09543'),
    ('Loshchilov, I., and Hutter, F. (2019).',
     'Decoupled Weight Decay Regularization. ICLR.',
     'https://arxiv.org/abs/1711.05101'),
    ('McCoy, R. T., Pavlick, E., and Linzen, T. (2019).',
     'Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in Natural Language Inference. ACL, 3428-3448.',
     'https://aclanthology.org/P19-1334/'),
    ('Poliak, A., Naradowsky, J., Haldar, A., Rudinger, R., and Van Durme, B. (2018).',
     'Hypothesis Only Baselines in Natural Language Inference. *SEM, 180-191.',
     'https://aclanthology.org/S18-2023/'),
    ('Swayamdipta, S., Schwartz, R., Lourie, N., Wang, Y., Hajishirzi, H., Smith, N. A., and Choi, Y. (2020).',
     'Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics. EMNLP, 9275-9293.',
     'https://aclanthology.org/2020.emnlp-main.746/'),
    ('Williams, A., Nangia, N., and Bowman, S. R. (2018).',
     'A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference. NAACL-HLT, 1112-1122.',
     'https://aclanthology.org/N18-1101/'),
]

def styles():
    font_dir = Path('C:/Windows/Fonts')
    if (font_dir/'times.ttf').exists():
        for name, file in [('Body','times.ttf'),('BodyBold','timesbd.ttf'),('BodyItalic','timesi.ttf')]:
            pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
        pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    else:
        for name, face in [('Body','Times-Roman'),('BodyBold','Times-Bold'),('BodyItalic','Times-Italic')]:
            pdfmetrics.registerFont(Font(name,face,'WinAnsiEncoding'))
        pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
    s=getSampleStyleSheet()
    for key in ['Normal','BodyText']:
        s[key].fontName='Body';s[key].fontSize=10.5;s[key].leading=14.5;s[key].spaceAfter=8
    for key in ['Heading1','Heading2']:
        s[key].fontName='BodyBold';s[key].textColor=colors.HexColor('#17201f')
        s[key].keepWithNext=True
    s['Heading1'].fontSize=15;s['Heading1'].leading=18;s['Heading1'].spaceAfter=12
    s['Heading2'].fontSize=11.5;s['Heading2'].leading=15;s['Heading2'].spaceBefore=12;s['Heading2'].spaceAfter=6
    s.add(ParagraphStyle(name='PaperTitle',fontName='BodyBold',fontSize=23,leading=27,spaceAfter=15))
    s.add(ParagraphStyle(name='Subtitle',fontName='BodyItalic',fontSize=11,leading=15,textColor=colors.HexColor('#52605a'),spaceAfter=12))
    s.add(ParagraphStyle(name='SmallNote',fontName='Body',fontSize=8.5,leading=11.5,spaceAfter=8,textColor=colors.HexColor('#46534d')))
    s.add(ParagraphStyle(name='Ref',fontName='Body',fontSize=9,leading=12,spaceAfter=10,leftIndent=12,firstLineIndent=-12))
    s.add(ParagraphStyle(name='Cell',fontName='Body',fontSize=9,leading=11))
    s.add(ParagraphStyle(name='Equation',fontName='Body',fontSize=10.5,leading=17,leftIndent=20,spaceAfter=5))
    s.add(ParagraphStyle(name='CaptionText',fontName='BodyItalic',fontSize=9,leading=12,spaceAfter=10))
    return s

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#c9cec9'));canvas.line(54,39,558,39)
    canvas.setFont('Body',8);canvas.setFillColor(colors.HexColor('#52605a'))
    canvas.drawString(54,26,'Leggieri | Dataset cartography for natural language inference')
    canvas.drawRightString(558,26,str(doc.page));canvas.restoreState()

def generate():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    s=styles();story=[]
    def p(text,style='BodyText'):story.append(Paragraph(text,s[style]))
    def h(text):p(text,'Heading2')
    def page(title):
        if story:story.append(PageBreak())
        p(title,'Heading1')
    def table(caption,headers,rows,widths,size=9):
        p(caption,'CaptionText')
        data=[[Paragraph(escape(str(c)),s['Cell']) for c in row] for row in [headers,*rows]]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eee7')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#52605a')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d6dcd5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.append(t);story.append(Spacer(1,12))

    p('Dataset Cartography for Robust Natural Language Inference','PaperTitle')
    p('Category-weighted DeBERTa training on MNLI and evaluation on HANS','Subtitle')
    p('Robert Leggieri · The University of Texas at Austin<br/>rjleggieri@utexas.edu')
    h('Abstract')
    p('This study investigates whether category-weighted training informed by dataset cartography can improve the robustness of DeBERTa-v3-base on natural language inference. We record training dynamics for 392,702 MNLI examples across five epochs, categorize examples by learning behavior, and incorporate category weights into cross-entropy loss. The selected configuration assigns weights of 0.5, 1.0, and 0.5 to easy, ambiguous, and hard examples, respectively, with a variability threshold of 0.2. HANS accuracy increases from 77.49% to 78.59%, while MNLI validation accuracy decreases from 88.91% to 88.47%. The improvement varies substantially across syntactic subcases, and several difficult constructions remain largely unsolved. Increasing the influence of hard examples is less effective than down-weighting them, motivating competing explanations involving annotation quality, ambiguity, and optimization. The findings support further investigation of training-data weighting while emphasizing the need for controlled model selection, repeated runs, and targeted error analysis.')
    h('1. Introduction')
    p('Natural language inference (NLI) asks whether a hypothesis is entailed by, contradicts, or is neutral with respect to a premise. The task provides a useful setting for studying the gap between benchmark performance and robust language understanding. A classifier can achieve high accuracy by exploiting regularities that correlate with labels in its training distribution, yet fail when those regularities no longer support the correct inference. Hypothesis-only baselines expose one form of this problem (Poliak et al., 2018), while HANS tests three fallible syntactic heuristics through controlled sentence pairs (McCoy et al., 2019).')
    p("Dataset cartography characterizes examples through a model's behavior over training epochs (Swayamdipta et al., 2020). Rather than treating all training examples as equally informative, the framework makes it possible to inspect regions that are learned consistently, inconsistently, or rarely. We use these signals to construct a category-weighted training objective. All examples remain in the training set; their contributions to the loss depend on their learning-region assignments.")

    p('Our objective is to examine whether this intervention improves challenge-set behavior while retaining useful in-domain performance. We evaluate both MNLI and HANS, inspect the subcases contributing to the aggregate result, and analyze the trade-off introduced by the selected weighting. This separates the observed performance change from stronger hypotheses about shortcut removal or the quality of difficult training examples.')

    page('2. Methodology')
    h('2.1 Datasets and evaluation scope')
    p('MNLI provides sentence pairs from multiple genres with entailment, neutral, and contradiction labels (Williams et al., 2018). We use 392,702 training examples. The validation comparison includes 9,815 examples: 3,479 contradiction, 3,123 neutral, and 3,213 entailment instances. Table 2 gives the corresponding class support alongside precision, recall, and F1 scores.')
    p('HANS contains 30,000 examples organized into 30 subcases spanning lexical overlap, subsequence, and constituent heuristics (McCoy et al., 2019). Each subcase contains 1,000 examples with a designated entailment or non-entailment label. These controlled constructions test cases where a superficial heuristic either supports or conflicts with the correct inference. Table 3 presents accuracy for every subcase as well as overall accuracy.')
    h('2.2 Model and training configuration')
    p('We use DeBERTa-v3-base, with 12 transformer layers, hidden size 768, and 12 attention heads. DeBERTa introduces disentangled attention (He et al., 2021), and DeBERTaV3 combines ELECTRA-style replaced-token detection with gradient-disentangled embedding sharing (He et al., 2023; Clark et al., 2020). These models build on encoder-based pretraining approaches exemplified by BERT (Devlin et al., 2019).')
    p('Training uses Hugging Face Transformers and PyTorch, a learning rate of 5 × 10<super>−5</super>, batch size 32, five epochs, and AdamW (Loshchilov and Hutter, 2019). Baseline and weighted models share the base Trainer configuration, with the category weights supplying the experimental intervention. Experiments run on an Intel Xeon W-2245 workstation with 32 GB RAM and an RTX 4080 GPU with 16 GB VRAM.')
    h('2.3 Training dynamics')
    p('A custom <font face="Courier">TrainingDynamicsCallback</font> recorded per-example logits and gold labels at each epoch end in JSON Lines files. For example i, let q(i,e) be the probability assigned to its gold label at epoch e and E = 5. The recorded measures were:')
    for text in [
        'Confidence: μ<sub>i</sub> = (1/E) ∑<super>E</super><sub>e=1</sub> q(i,e)',
        'Variability: σ<sub>i</sub> = √[(1/E) ∑<super>E</super><sub>e=1</sub> (q(i,e) − μ<sub>i</sub>)<super>2</super>]',
        'Correctness: c<sub>i</sub> = (1/E) ∑<super>E</super><sub>e=1</sub> 1[argmax<sub>y</sub> p(y | x<sub>i</sub>,e) = gold<sub>i</sub>]',
    ]:
        p(text,'Equation')
    p('Confidence concerns the gold label, not the most probable label. Variability measures changes across the recorded epochs, and correctness is the fraction of epochs with a correct predicted label. These are properties of a model and training trajectory, rather than intrinsic annotations of difficulty.','SmallNote')

    page('2. Methodology (continued)')
    h('2.4 Data map and learning regions')
    story.append(Image(str(FIGURE),width=504,height=302.4))
    p('Figure 1. MNLI data map generated in this study from DeBERTa-v3-base training dynamics over five epochs. Variability is on the horizontal axis, confidence on the vertical axis, and color denotes correctness.','CaptionText')
    p('Easy examples have high, stable gold-label confidence; hard examples have low, stable confidence; ambiguous examples exhibit greater variability. Figure 1 shows the relationship between these measures and correctness. Region names describe learning behavior relative to this model and training trajectory. They do not establish intrinsic difficulty or annotation quality, and their interpretation depends on the categorization thresholds.')
    h('2.5 Category-weighted loss')
    p('Each example receives a weight according to its assigned category. A <font face="Courier">WeightedMNLI_Dataset</font> exposes weights alongside model inputs and labels, and a <font face="Courier">WeightedLossTrainer</font> overrides loss computation. For example i with C possible labels, the weighted cross-entropy contribution is:')
    p('L<sub>i</sub> = w<sub>category(i)</sub> · [−∑<super>C</super><sub>c=1</sub> y<sub>i,c</sub> log p<sub>i,c</sub>]','Equation')
    p('The selected weights are easy = 0.5, ambiguous = 1.0, and hard = 0.5, with variability threshold 0.2. We explore easy weights from 0.0 to 0.5, ambiguous weights from 1.0 to 1.2, hard weights from 0.0 to 2.0, and variability thresholds from 0.15 to 0.30. Category assignments are derived from the baseline training dynamics and remain fixed during weighted training. The intervention therefore changes the relative influence of learning regions without introducing online reassignment.')
    p('The comparison evaluates category weighting within a shared training configuration. Weighting changes both the balance of examples and the magnitude of their loss contributions; loss normalization and effective optimization scale are relevant controls for interpreting the intervention.','SmallNote')

    page('3. Results: MNLI')
    p('Tables 1 and 2 compare the baseline and selected category-weighted models. The baseline model identifier is <font face="Courier">deberta-v3-base_mnli</font>; the weighted model identifier is <font face="Courier">deberta-v3-base_cart_(0.5-1.0-0.5)_mnli</font>.')
    table('Table 1. MNLI evaluation metrics for the baseline and category-weighted models.', ['Metric','Base model','Re-weighted model'],MNLI_METRICS,[264,120,120])
    table('Table 2. MNLI classification performance and class support.', ['Model','Class','Precision','Recall','F1','Support'],MNLI_CLASSES,[83,114,78,70,70,89])
    h('3.1 Accuracy and loss are different observations')
    p('MNLI accuracy decreases from 88.91% to 88.47%, a decline of 0.44 percentage points, while evaluation loss decreases from 0.6366 to 0.6101. Lower cross-entropy loss can coexist with lower accuracy because the two metrics describe different properties of predictions. The former depends on the probabilities assigned to labels; the latter depends on the highest-scoring label. The loss reduction alone does not establish improved calibration.')
    p('The class-level results show small declines in precision, recall, and F1 across all three labels. The aggregate accuracy change therefore accompanies a broadly distributed in-domain cost rather than an isolated gain for one class. Small differences between rounded class recalls and aggregate accuracy are compatible with rounding. Runtime and throughput are measurements from these evaluations; without repeated timing trials, they do not establish a speed advantage.')

    page('3. Results: HANS')
    p('Table 3. HANS subcase accuracy for the baseline and category-weighted models. Each subcase contains 1,000 examples.','CaptionText')
    data=[['Heuristic','Subcase','Base','Re-weighted'],*HANS]
    cell=ParagraphStyle('HansCell',parent=s['Cell'],fontSize=8,leading=9)
    t=Table([[Paragraph(escape(c),cell) for c in row] for row in data],colWidths=[88,266,70,80],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eee7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#52605a')),('LINEBELOW',(0,-1),(-1,-1),.7,colors.HexColor('#52605a')),('TOPPADDING',(0,0),(-1,-1),3.3),('BOTTOMPADDING',(0,0),(-1,-1),3.3),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]))
    story.append(t)
    p('The observed overall change is +1.10 percentage points. Gains and regressions vary by subcase. The large residual failures in several non-entailment constructions remain important even after the aggregate improvement.','SmallNote')

    page('4. Discussion')
    h('4.1 A modest robustness trade-off')
    p('The clearest result is a shift in performance between evaluation distributions. HANS accuracy improves by 1.10 percentage points while MNLI accuracy declines by 0.44 points. That is a potentially useful trade-off for an application prioritizing the HANS-like constructions, but its value depends on actual error costs and the deployment distribution. The experiment does not identify a universally better model.')
    p('The result is consistent with the possibility that changing the relative influence of learning regions changes what the classifier relies on. It does not isolate that mechanism. Category weighting also changes the effective training objective and gradient contributions; alternative explanations include regularization, altered optimization, and the balance of examples contributing to learning. A uniform-weight control with comparable effective loss scaling, plus controlled ablations, would help distinguish these explanations.')
    h('4.2 Aggregate accuracy hides persistent failures')
    p('Table 3 shows that some subcases are already near ceiling while others remain near zero. For example, <font face="Courier">cn_after_if_clause</font> moves from 0.00% to 1.40%, and <font face="Courier">cn_disjunction</font> from 0.40% to 1.50%. These are improvements in the recorded runs, but they do not solve those constructions. Similarly, <font face="Courier">sn_NP/S</font> changes from 0.10% to 0.00%. A higher overall average should not obscure continued systematic failure.')
    p('The strongest listed constituent gain is <font face="Courier">cn_embedded_under_verb</font>, from 58.60% to 68.50%. Other rows regress, including <font face="Courier">ce_embedded_under_since</font> and <font face="Courier">cn_embedded_under_if</font>. The intervention therefore redistributes errors unevenly. Examining error pairs, confusion patterns, and the linguistic content of improved and degraded examples would provide stronger evidence than the aggregate alone.')
    p('Perfect accuracy on <font face="Courier">le_passive</font> indicates successful classification of those examples, but does not by itself reveal the decision rule used. A claim of heuristic reliance requires contrasts where the heuristic succeeds and fails. HANS is useful because its controlled constructions permit these behavioral comparisons (McCoy et al., 2019). The mixed subcase results call for examining patterns of changed decisions rather than inferring a general change in linguistic competence from a single score.')
    h('4.3 Difficulty is a model-dependent signal')
    p('The data map is useful as an instrument for inquiry, rather than a final judgment of example quality. Five recorded epochs provide only a short trajectory, and the same example may move between regions under different seeds, checkpoints, learning rates, or architectures. Threshold-based categories discretize continuous signals. A threshold of 0.2 is a selected experimental setting, not a transferable constant established by this study.')

    page('4. Discussion (continued)')
    h('4.4 Hard-example weighting does not diagnose label errors')
    p('Increasing hard-example weights worsens both standard and challenge-set performance in the explored configurations. The selected model down-weights hard examples as well as easy examples, despite the initial expectation that difficult examples would provide useful learning signal. This observation challenges a simple equation of training difficulty with training value, but does not identify why emphasizing the hard region is detrimental.')
    p('Swayamdipta et al. (2020) connect learning regions with data quality, making annotation noise one plausible explanation. Alternatives include genuine linguistic ambiguity, rare but correctly labeled constructions, imperfect category rules, limitations of the model, and unstable optimization. This experiment does not estimate a label-error rate or include a human annotation audit. Down-weighting could suppress valuable rare examples as well as noisy ones.')
    p('A useful follow-up would sample examples from each region for blinded review, separate annotation disagreement from clear errors, and compare region composition across labels and genres. Weighting should then be evaluated against those audits. Low confidence in a gold label is a reason to investigate that example, not permission to treat it as mislabeled.')
    h('4.5 Configuration selection and evaluation independence')
    p('We explore multiple category weights and variability thresholds before selecting the configuration presented here. The comparison is exploratory: it does not supply a separate final challenge-set estimate after configuration selection. HANS performance consequently provides evidence about behavior on this benchmark, but cannot establish how much of the selected gain transfers to an independently evaluated distribution.')
    p('Repeated inspection of a benchmark can make the best observed result optimistic, even when the benchmark is never used for gradient updates. A follow-up should distinguish training data, configuration-selection data, and final evaluation data. It should prerecord which metric determines selection and retain the outcomes of all candidates. If HANS informs design choices, a separate challenge set or a reserved evaluation protocol is needed for a stronger final claim.')
    h('4.6 Uncertainty and paired evidence')
    p('The results compare one baseline model with one selected weighted model, without an estimate of variability across repeated training seeds. The observed improvement therefore does not establish that the intervention reliably improves performance across training runs. Paired item predictions could reveal which decisions change, while repeated runs would quantify sensitivity to stochastic training. These address different sources of uncertainty and should both inform a stronger evaluation.')
    p('HANS examples are generated from structured subcases. Treating all 30,000 observations as independent, identically distributed deployment cases would overstate the breadth of the evidence. An uncertainty analysis should specify its sampling unit and account for the relationship between templates, subcases, and the target population. Statistical significance and population-level confidence intervals are not established by the aggregate accuracies in this study.')

    page('5. Limitations and future work')
    h('5.1 Scope of the comparison')
    p('The comparison is limited to one model family, one training corpus, and one syntactic challenge set. It does not isolate category weighting from changes in effective optimization scale, exhaustively characterize sensitivity to categorization rules, or quantify training-seed variability. The observed trade-off should therefore be evaluated as a result for this configuration rather than a general property of dataset cartography.')
    p('Reproducible follow-up experiments should specify dataset versions and exact split identifiers, preprocessing and tokenization, category thresholds, initialization, seeds, and loss normalization. MNLI uses three labels whereas HANS distinguishes entailment from non-entailment; the evaluation protocol should also distinguish collapsing predicted labels from aggregating non-entailment probabilities. These implementation choices should be fixed before comparing candidate models.')
    h('5.2 A focused follow-up design')
    p('<b>Establish an explicit selection protocol.</b> Separate training, configuration selection, and final evaluation; define the selection objective in advance; and retain full candidate results, checkpoints, and paired prediction artifacts. This permits both auditing of the selected configuration and evaluation on data that did not guide its selection.')
    p('<b>Isolate the weighting components.</b> Compare unweighted training, easy-only down-weighting, hard-only down-weighting, and combined weighting with matched training settings. Include a control for uniform loss scaling and repeat each comparison across seeds to estimate the stability of the trade-off.')
    p('<b>Investigate learning regions and changed decisions.</b> Audit a stratified sample from each region, distinguish annotation disagreement from clear errors, and examine HANS predictions that improve or regress. Per-subcase behavior and in-domain error costs should guide interpretation alongside aggregate accuracy.')
    p('<b>Evaluate transfer independently.</b> Freeze design choices before testing on a separate challenge distribution or domain dataset. Annotation quality and application-specific error costs should determine whether the resulting trade-off is useful.')
    h('5.3 Implications for applied NLP')
    p('The practical contribution is a workflow for connecting training-data inspection with a testable intervention: instrument training, examine example-level behavior, implement a weighting rule, and compare performance across distributions. The same workflow can guide investigation of a domain-specific text classifier, but any operational benefit requires evidence from that domain. Robustness on selected linguistic constructions does not by itself establish calibration, demographic fairness, or safety.')
    p('6. Conclusion','Heading1')
    p('Category-weighted DeBERTa training increases HANS accuracy from 77.49% to 78.59%, alongside a MNLI accuracy decline from 88.91% to 88.47%. The subcase analysis reveals both useful improvements and persistent failures, while the weighting experiments motivate closer examination of what makes a training example informative. Dataset cartography provides a structured basis for that investigation. Establishing the reliability and mechanism of the observed gain requires controlled ablations, repeated runs, annotation audits, and independent evaluation.')

    page('References')
    for authors,title,url in REFERENCES:
        p(f'{escape(authors)} {escape(title)} <link href="{url}" color="#123f38">{url}</link>','Ref')

    doc=SimpleDocTemplate(str(OUTPUT),pagesize=LETTER,leftMargin=54,rightMargin=54,topMargin=48,bottomMargin=54,
        title='Dataset Cartography for Robust Natural Language Inference',author='Robert Leggieri',
        subject='Category-weighted DeBERTa training on MNLI and evaluation on HANS')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    for dest in [ROOT/'docs/Making-DeBERTa-Smarter.pdf',ROOT/'public/docs/Making-DeBERTa-Smarter.pdf']:
        shutil.copyfile(OUTPUT,dest)
    print(f'Generated {OUTPUT} ({len(PdfReader(str(OUTPUT)).pages)} pages)')

if __name__=='__main__':generate()
