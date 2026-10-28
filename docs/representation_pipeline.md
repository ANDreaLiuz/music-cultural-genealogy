# Representation pipeline

The research distinguishes four stages:

**Recording → representation → estimated relationship → independent validation**

A recording has identity and context: edition, performance, production and temporal extent. A representation compresses aspects of that signal. A distance measure then creates a particular notion of proximity. Validation asks whether that proximity answers the intended musical question.

Earlier prototypes used established audio descriptors and pretrained embeddings. Such representations can support exploratory analysis without assigning a musical meaning to every learned coordinate. Average descriptors can also obscure when events occur; an ordered view and a pooled view need not support the same inference.

Normalization, excerpt selection, temporal scope and the relative influence of feature groups all matter. Comparing raw distance magnitudes across different representations does not create a common perceptual scale. Familiarity, artist identity, mastering and recording quality can provide competing explanations for an apparent relationship.

The portfolio illustration replaces audio with two deliberately constructed feature views named **surface** and **pattern**. These labels are teaching devices. They are not measured musical attributes, audio embeddings, validated timbre and harmony factors or a new representation method.

The toy score is a weighted mean of two within-view cosine similarities. It illustrates sensitivity to a representation choice; it supplies no model accuracy or evidence of perceptual disentanglement.
