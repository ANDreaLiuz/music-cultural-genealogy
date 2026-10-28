# Communities, neighborhoods and hierarchies

A neighborhood graph links recordings under a specified representation and distance. A community algorithm may summarize the density of that graph. A hierarchy organizes nested groupings under a separate clustering rule. Each construction answers a different computational question.

The historical engineering line used Leiden on a neighborhood graph and computed Ward clustering separately. Community labels annotated a tree; the labels did not generate its hierarchy. A Ward branch is not evidence of an ancestor, and a hard community assignment is not a claim that a recording belongs to only one cultural tradition.

Useful checks include sensitivity to parameters and random seeds, recording and artist dependence, temporal windows, normalization, alternative representations and the stability of local neighborhoods. A visually distinct map is insufficient evidence of a stable structure.

The standalone synthetic explorer performs **no community detection or hierarchical clustering**. It draws an undirected union of top-k neighbors above a threshold. Its node colors are designer-assigned synthetic surface groups, not discovered communities. Node positions follow a fixed circular layout, not an embedding, tree or geographic map.

Changing its controls changes a toy graph. It cannot demonstrate that Leiden, Ward or any research method succeeded or failed on real music.
