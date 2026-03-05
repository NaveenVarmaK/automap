#!/bin/bash
# patch_morph_kgc.sh
# Applies compatibility patches to morph-kgc for pandas>=2.0 and numpy>=2.0
# Run this once after `uv sync`

set -e

MORPH_PATH=$(python -c "import morph_kgc; import os; print(os.path.dirname(morph_kgc.__file__))")
echo "Patching morph-kgc at: $MORPH_PATH"

# Patch 1: pandas 2.0 — value_counts() no longer supports integer index access
sed -i "s/\.value_counts()\[0\]/\.value_counts().iloc[0]/g" \
    "$MORPH_PATH/mapping/mapping_partitioner.py"
echo "Patch 1 applied: mapping_partitioner.py (pandas 2.0 fix)"

# Patch 2: numpy 2.0 — np.NaN was removed, use np.nan
grep -rl "np\.NaN" "$MORPH_PATH" --include="*.py" | while read f; do
    sed -i "s/np\.NaN/np.nan/g" "$f"
    echo "Patch 2 applied: $f (numpy 2.0 fix)"
done

echo "All patches applied successfully."