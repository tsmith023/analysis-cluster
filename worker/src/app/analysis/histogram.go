package analysis

type bin struct {
	value float64
	count float64
}

type NumericHistogram struct {
	bins    []bin
	maxbins int
	total   uint64
}

// NewHistogram returns a new NumericHistogram with a maximum of n bins.
//
// There is no "optimal" bin count, but somewhere between 20 and 80 bins
// should be sufficient.
func NewHistogram(n int) *NumericHistogram {
	return &NumericHistogram{
		bins:    make([]bin, 0),
		maxbins: n,
		total:   0,
	}
}

func (h *NumericHistogram) Add(n float64) {
	defer h.trim()
	h.total++
	for i := range h.bins {
		if h.bins[i].value == n {
			h.bins[i].count++
			return
		}

		if h.bins[i].value > n {

			newbin := bin{value: n, count: 1}
			head := append(make([]bin, 0), h.bins[0:i]...)

			head = append(head, newbin)
			tail := h.bins[i:]
			h.bins = append(head, tail...)
			return
		}
	}

	h.bins = append(h.bins, bin{count: 1, value: n})
}

// trim merges adjacent bins to decrease the bin count to the maximum value
func (h *NumericHistogram) trim() {
	for len(h.bins) > h.maxbins {
		// Find closest bins in terms of value
		minDelta := 1e99
		minDeltaIndex := 0
		for i := range h.bins {
			if i == 0 {
				continue
			}

			if delta := h.bins[i].value - h.bins[i-1].value; delta < minDelta {
				minDelta = delta
				minDeltaIndex = i
			}
		}

		// We need to merge bins minDeltaIndex-1 and minDeltaIndex
		totalCount := h.bins[minDeltaIndex-1].count + h.bins[minDeltaIndex].count
		mergedbin := bin{
			value: (h.bins[minDeltaIndex-1].value*
				h.bins[minDeltaIndex-1].count +
				h.bins[minDeltaIndex].value*
					h.bins[minDeltaIndex].count) /
				totalCount, // weighted average
			count: totalCount, // summed heights
		}
		head := append(make([]bin, 0), h.bins[0:minDeltaIndex-1]...)
		tail := append([]bin{mergedbin}, h.bins[minDeltaIndex+1:]...)
		h.bins = append(head, tail...)
	}
}
