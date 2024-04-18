"""
STORM pipeline pre-writing stage:
Collect information grounded on search engine and organize information into a detailed outline.

Output will be structured as below
args.output_dir/
    topic_name/  # topic_name will follow convention of underscore-connected topic name w/o space and slash
        conversation_log.json    # Log of information-seeking conversation
        raw_search_results.json  # Raw search results from search engine
        direct_gen_outline.txt   # Outline directly generated with LLM's parametric knowledge
        storm_gen_outline.txt    # Outline refined with collected information
"""

import os
from argparse import ArgumentParser

import pandas as pd
from engine import DeepSearchRunnerArguments, DeepSearchRunner
from modules.utils import MyOpenAIModel, load_api_key, LLMConfigs
from tqdm import tqdm


def main(args):
    load_api_key()
    llm_configs = LLMConfigs()
    llm_configs.init()
    engine_args = DeepSearchRunnerArguments(
        output_dir=args.output_dir,
        max_conv_turn=args.max_conv_turn,
        max_perspective=args.max_perspective,
        search_top_k=args.search_top_k,
        disable_perspective=args.disable_perspective,

    )
    runner = DeepSearchRunner(engine_args, llm_configs)

    if args.input_source == 'console':
        topic = input('Topic: ')
        ground_truth_url = input('Ground truth url (will be excluded from source): ')
        runner.run(topic=topic,
                   ground_truth_url=ground_truth_url,
                   do_research=args.do_research,
                   do_generate_outline=True,
                   do_generate_article=False,
                   do_polish_article=False)
        runner.post_run()
    else:
        data = pd.read_csv(args.input_path)

        for _, row in tqdm(data.iterrows(), total=len(data)):
            topic = row['topic']
            ground_truth_url = row['url']
            runner.run(topic=topic,
                       ground_truth_url=ground_truth_url,
                       do_research=args.do_research,
                       do_generate_outline=True,
                       do_generate_article=False,
                       do_polish_article=False)
            runner.post_run()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--max-conv-turn', type=int, default=5,
                        help='Maximum number of questions in conversational question asking.')
    parser.add_argument('--max-perspective', type=int, default=5,
                        help='Maximum number of perspectives to consider in perspective-guided question asking.')
    parser.add_argument('--search-top-k', type=int, default=10,
                        help='Top k search results to consider for each search query.')
    parser.add_argument('--disable-perspective', action='store_true',
                        help='If True, disable perspective-guided question asking; set True only for ablation study.')
    parser.add_argument('--do-research', action='store_true',
                        help='If True, simulate conversation to research the topic; otherwise, load the results.')
    parser.add_argument('--input-source', type=str, choices=['console', 'file'],
                        help='Where does the input come from.')
    parser.add_argument('--input-path', type=str,
                        help='Using csv file to store topic and ground truth url at present.')
    parser.add_argument('--output-dir', type=str, default='../results',
                        help='Directory to store the outputs.')

    main(parser.parse_args())
