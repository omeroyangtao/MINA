# MINA: Multimodal Intention Analysis of Social Media Posts via LLM-Guided Audio-Visual-Text Reasoning

This repository provides the benchmark data for our paper **MINA: Multimodal Intention Analysis of Social Media Posts via LLM-Guided Audio-Visual-Text Reasoning**.

## Overview

MINA is designed for **implicit intention understanding** in social media posts.  
Unlike previous approaches that mainly rely on text or image-text pairs, MINA jointly reasons over **text, images, videos, and audio** (https://pan.baidu.com/s/1aW8IloeB1jqWAUj-pS1snA?pwd=7ci5) to better capture the complex and subtle intentions expressed by users in real-world social media scenarios.

To further handle cross-modal inconsistency and varying modality importance, MINA introduces an **LLM-guided intention analysis strategy generation and evaluation mechanism**, which dynamically prioritizes multimodal signals according to their relevance, analytical depth, and clarity for each social media post.

Based on this framework, we build a benchmark on **Twibot-22 tweets** for evaluating the intention reasoning ability of large language models and multimodal large language models. The benchmark contains high-quality multimodal intention knowledge derived from posts with **textual, visual, video, and audio** information, supporting systematic evaluation of open-domain social media intention understanding.

## Framework

The overall framework of MINA is shown below. MINA first extracts multimodal features from text, image, audio, and video inputs. Then, an LLM-guided strategy generation and evaluation module dynamically produces and refines intention analysis strategies. The selected strategy guides the LLM to generate user intentions, which are further filtered to construct high-quality multimodal intention knowledge.

![MINA Framework](./assets/MINA_framework.png)

## Contribution

- Propose **MINA**, a multimodal intention analysis framework for social media posts.
- Integrate **text, image, video, and audio** signals for unified intention reasoning.
- Design an **LLM-guided intention analysis strategy generation and evaluation mechanism** to dynamically prioritize multimodal information.
- Introduce a **role-play-based intention filtering strategy** to automatically remove unreasonable or irrelevant generated intentions.
- Construct a benchmark based on **Twibot-22 tweets** to evaluate model performance on social media intention understanding.
- Demonstrate that MINA-generated intention knowledge can benefit downstream social media analysis tasks such as bot detection and sarcasm detection.
