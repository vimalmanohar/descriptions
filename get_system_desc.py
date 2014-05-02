#!/usr/bin/python
import re, sys, os

def system2string(system_type,lang_pack,lexicon,system2sections,section2string):
    if system_type == 'DNN' and lang_pack == 'FullLP':
        system_string = 'DNN-BASIC'
    elif system_type == 'DNN' and lang_pack == 'LimitedLP':
        system_string = 'DNN'
    elif system_type == 'DNN_MPE':
        system_string = 'DNN'
    elif system_type == 'PLP':
        system_string = 'SGMM'
    elif system_type == 'BNF':
        system_string = 'BNF'
    elif system_type == 'BNF_SEMISUP':
        system_string = 'BNF-SEMISUPX'
    elif system_type == '4way comb':
        system_string = '4-way combination'
    elif system_type == '8way comb':
        system_string = '8-way combination'
    elif system_type == 'DNN_RESCORED':
        system_string = 'DNN-RESCORED'
    elif system_type == 'BNF_RESCORED':
        system_string = 'BNF-RESCORED'
    else:
        sys.stderr.write('Unknown system %s\n' % system_type)
        sys.exit(1)

    if system_string == 'DNN-BASIC':
        temp_string = 'DNN'
    else:
        temp_string = system_string

    sections = system2sections[(system_string,lang_pack)]

    if system_type == '4way comb':
        sub_string = 'PLP, DNN, BNF and BNF-Semisupervised systems'
        if lang_pack == 'FullLP':
            sub_string = 'PLP, BNF, DNN and DNN-Sequence-Trained systems'
        if lexicon == 'basic':
            desc_string = '%s of 4 sub-systems: %s, each of them using the provided BaseLR lexicon.' % (temp_string, sub_string)
        elif lexicon == 'extended':
            desc_string = '%s of 4 sub-systems: %s, each of them using the extended lexicon of Section %s.' % (temp_string, sub_string, section2string['4.4'])
        else:
            desc_string = '%s of 4 sub-systems: %s, each of them using the combined lexicon of Section %s.' % (temp_string, sub_string, section2string['4.4'])
        desc_string += ' The individual sub-systems are described in Sections %s of the complete system description' % ', '.join(sections[0])
        return desc_string
    if system_type == '8way comb':
        sub_string = 'PLP, DNN, BNF and BNF-Semisupervised systems'
        if lang_pack == 'FullLP':
            sub_string = 'PLP, BNF, DNN and DNN-Sequence-Trained systems'
        desc_string = '%s of 4 sub-systems: %s, each with two versions of lexicon:  extended lexicon of Section %s and the provided BaseLR lexicon.' % (temp_string, sub_string, section2string['4.4'])
        desc_string += ' The individual sub-systems are described in Sections %s of the complete system description' % ', '.join(sections[0])
        return desc_string

    if lexicon == 'basic':
        desc_string = '%s system using the provided BaseLR lexicon' % temp_string
    elif lexicon == 'extended':
        desc_string = '%s system using the extended lexicon of Section %s' % (temp_string, section2string['4.4'])
    elif lexicon == 'combined':
        desc_string = '%s system using the combined lexicon from both the extended lexicon of Section %s and segmental system of Section %s' % (temp_string, section2string['4.4'],section2string['4.18'])
    else:
        sys.stderr.write('Unknown lexicon %s\n' % lexicon)
        sys.exit(1)

    if len(sections[0]) == 1:
        desc_string += ', as described in Section %s of the complete system description' % ', '.join(sections[0])
    else:
        desc_string += ', as described in Sections %s of the complete system description' % ', '.join(sections[0])
    if len(sections) > 1:
        if len(sections[1]) == 1:
            desc_string += '. This sub-system includes Section %s' % ', '.join(sections[1])
        else:
            desc_string += '. This sub-system includes Sections %s' % ', '.join(sections[1])
    if len(sections) > 2:
        if len(sections[2]) == 1:
            desc_string += ' but excludes Section %s' % ', '.join(sections[2])
        else:
            desc_string += ' but excludes Sections %s' % ', '.join(sections[2])

    if system_type == 'BNF_SEMISUP':
        desc_string += '. The semi-supervised training involves using the FullLP and "untranscribed" data without the transcripts. The data is segmented automatically and decoded using the DNN (Section %s) system to get the 1-best output. The state-level posteriors on this 1-best path from both the DNN and PLP (Section %s) systems are interpolated and used to do frame-selection. Only the frames that have a state-level posterior above a threshold (we use a low threshold of 0.35 for this case) are selected and used for cross-entropy neural network training' % (section2string['4.9'], section2string['4.8'])
    return desc_string

def type2string(system_type,lang_pack):
    if system_type == 'DNN':
        if lang_pack == 'LimitedLP':
            return 'DNN'
        else:
            return 'DNN-BASIC'
    if system_type == 'DNN_MPE':
        return 'DNN'
    if system_type in ('PLP','BNF'):
        return system_type
    if system_type == '4way comb':
        return 'comb-4way'
    if system_type == '8way comb':
        return 'comb-8way'
    if system_type == 'BNF_SEMISUP':
        return 'BNF-SEMISUPX'
    if system_type == 'DNN_RESCORED':
        return 'DNN-RESCORED'
    if system_type == 'BNF_RESCORED':
        return 'BNF-RESCORED'
    sys.stderr.write('Unknown system type %s\n' % system_type)
    sys.exit(1)

def condition2dir(lang_pack,lexicon):
    if lexicon in ('base','basic'):
        return 'NTAR-%s-basic' % lang_pack
    if lexicon in ('Extended','extended','8way','combined'):
        return 'NTAR-%s-extlex' % lang_pack
    print (lexicon)
    assert (False)

def read_sections(sections_file,sections_map):
    type2type = {
            'bnf': 'BNF',
            'dnnbasic': 'DNN-BASIC',
            'dnn': 'DNN',
            'comb4': '4-way combination',
            'bnfsemisup': 'BNF-SEMISUPX',
            'comb8': '8-way combination',
            'plp': 'SGMM',
            'dnn_rescore':'DNN-RESCORED',
            'bnf_rescore':'BNF-RESCORED'}

    system2sections = {}

    section2string = {}
    for line in open(sections_map):
        splits = line.strip().split(',')
        section2string[splits[0]] = '[' + splits[0] + ' ' + splits[1] + ']'

    for line in open(sections_file).readlines():
        splits = line.strip().split(',')

        if splits[0].split('-')[0] == 'full':
            lang_pack = 'FullLP'
        elif splits[0].split('-')[0] == 'lim':
            lang_pack = 'LimitedLP'
        else:
            sys.stderr.write('Unknown pack %s\n' % splits[0].split('-')[0])
            sys.exit(1)

        system_type = type2type[splits[0].split('-')[2]]

        system2sections[(system_type,lang_pack)] = [tuple([ section2string[x] for x in splits[1].split(':') ])]
        if len(splits) > 2:
            system2sections[(system_type,lang_pack)].append(tuple([ section2string[x] for x in splits[2].split(':') ]))
        if len(splits) > 3:
            system2sections[(system_type,lang_pack)].append(tuple([ section2string[x] for x in splits[3].split(':') ]))

    return [section2string, system2sections]

if len(sys.argv) == 4:
    in_file = open(sys.argv[1])
    section2string_file = sys.argv[2]
    system2sections_file = sys.argv[3]
elif len(sys.argv) == 3:
    in_file = sys.stdin
    section2string_file = sys.argv[1]
    system2sections_file = sys.argv[2]
else:
    sys.stderr.write("Num arguments < 2")
    sys.exit(1)


lang_id2lang = {
        102: '102-assamese',
        103: '103-bengali',
        201: '201-haitian',
        203: '203-lao',
        206: '206-zulu',
        204: '204-tamil'
        }

suff_stats = {}
i=-1

for line in in_file.readlines():
    i += 1
    if i == 0:
        continue

    try:
        splits = line.strip().split(',')
        lang = splits[0]
        lang_id = int(lang.split('-')[0])
        lang = lang_id2lang[lang_id]
        lang_pack = splits[1] + 'LP'
        lexicon = splits[2]
        system_string = splits[3]
        total_time = splits[6]
        elapsed_time = splits[7]
        total_elapsed_time = splits[8]
        total_gpu_time = splits[9]
    except IndexError:
        sys.stderr.write(line)
        sys.exit(1)

    if re.search('Ingestion', system_string):
        ingestion = True
    elif re.search('Search', system_string):
        ingestion = False
    else:
        sys.stderr.write('Unable to parse %s' % system_string)
        sys.exit(1)

    has_gpu = False
    if re.search('GPU', system_string):
        has_gpu = True

    m = re.search('(.*) (Ingestion|Search).*', system_string)
    system_type = m.group(1)

    suff_stats.setdefault((lang,lang_pack,lexicon,system_type), [0]*6)
    if ingestion and not has_gpu:
        suff_stats[(lang,lang_pack,lexicon,system_type)][0] = elapsed_time
        suff_stats[(lang,lang_pack,lexicon,system_type)][1] = total_time
    if ingestion and has_gpu:
        suff_stats[(lang,lang_pack,lexicon,system_type)][0] = total_elapsed_time
        suff_stats[(lang,lang_pack,lexicon,system_type)][2] = total_gpu_time
    if not ingestion and not has_gpu:
        suff_stats[(lang,lang_pack,lexicon,system_type)][3] = elapsed_time
        suff_stats[(lang,lang_pack,lexicon,system_type)][4] = total_time
        suff_stats[(lang,lang_pack,lexicon,system_type)][5] = '0:00:00'

section2string, system2sections = read_sections(section2string_file, system2sections_file)
lang_id2string = {
        102: '102b-v0.5a',
        103: '103b-v0.4b',
        201: '201b-v0.2b',
        203: '203b-v3.1a',
        206: '206b-v0.1e',
        204: '204b-v1.1b'
        }

for lang,lang_pack,lexicon,system_type in suff_stats:
    lang_id = int(lang.split('-')[0])
    assert(lang_id in (102,103,201,203,206,204))
    if lang_pack not in ('FullLP','LimitedLP'):
        sys.stderr.write(lang_pack)
        sys.exit(1)
    assert(lexicon in ('basic','extended','combined','8way','8-way') or sys.stderr.write(lexicon))

    datadef = "DATADEF:==BaseLR{%d%s}:AM{%d%s},LM{%d%s},PRON{%d%s},AR{None}" % (lang_id, lang_pack, lang_id, lang_pack, lang_id, lang_pack, lang_id, lang_pack)

    ingestion_elapsed_time = suff_stats[(lang,lang_pack,lexicon,system_type)][0]
    ingestion_cpu_time = suff_stats[(lang,lang_pack,lexicon,system_type)][1]
    ingestion_gpu_time = suff_stats[(lang,lang_pack,lexicon,system_type)][2]

    search_elapsed_time = suff_stats[(lang,lang_pack,lexicon,system_type)][3]
    search_cpu_time = suff_stats[(lang,lang_pack,lexicon,system_type)][4]
    search_gpu_time = suff_stats[(lang,lang_pack,lexicon,system_type)][5]

    system_string = 'kaldi-' + type2string(system_type,lang_pack)
    if lexicon == 'basic':
      system_string += '-BASIC'
    elif lexicon == 'combined':
      system_string += '-COMBINED'
    else:
      system_string += '-EXTLEX'

    system_string += '_2'

    exp_id = 'KWS14_RADICAL_IARPA-babel%s_conv-eval_BaEval_KWS_c-%s' % (lang_id2string[lang_id],system_string)

    if lexicon == '8-way':
        lexicon = '8way'

    os.system('mkdir -p desc')
    os.system('mkdir -p desc/%s' % lang)
    os.system('mkdir -p desc/%s/%s' % (lang, condition2dir(lang_pack,lexicon)))
    out_handle = open('desc/%s/%s/%s.txt' % (lang, condition2dir(lang_pack,lexicon), exp_id), 'w')

    out_handle.write(
"""Description of Kaldi subsystems

This is a description of one of the kaldi sub-systems. For reference, see the complete system description, part of the submission 204-tamil/KWS14_RADICAL_IARPA-babel204b-v1.1b_conv-eval_BaEval_KWS_c-kaldi-comb-5way_2.kwslist.xml (Internal SHA256 : 40ea1a5c116307d68a3d9818c8a149604ed3a79000f290437410600783e2e9a0)

1. Abstract
This file contains timing analysis and data definition for the %s.

2. Data definition

%s

3. Timing Analysis

Ingestion Elapsed Time (hh:mm:ss) - %s
Ingestion Total CPU Time (hh:mm:ss) - %s
Ingestion Total GPU Time (hh:mm:ss) - %s

Ingestion Maximum CPU Memory (gbytes) - 192
Ingestion Maximum GPU Memory (gbytes) - 16

Search Elapsed Time (hh:mm:ss) - %s
Search Total CPU Time (hh:mm:ss) - %s
Search Total GPU Time (hh:mm:ss) - %s

Search Maximum CPU Memory (gbytes) - 32
Search Maximum GPU Memory (gbytes) - 16
""" % (system2string(system_type,lang_pack,lexicon,system2sections,section2string),datadef, ingestion_elapsed_time, ingestion_cpu_time, ingestion_gpu_time, search_elapsed_time, search_cpu_time, search_gpu_time) )
    out_handle.close()
