package main

import "testing"

func TestSafePathComponent(t *testing.T) {
	cases := map[string]string{
		"../../Library/LaunchAgents/x.plist": "x.plist",
		"..":                                 "_",
		".hidden":                            "hidden",
		"3B9002D17631D1BF14C9":               "3B9002D17631D1BF14C9",
		"231284727111889@lid":                "231284727111889@lid",
		"a/b\\c:d e.pdf":                     "b_c_d_e.pdf",
	}
	for in, want := range cases {
		if got := safePathComponent(in); got != want {
			t.Errorf("safePathComponent(%q) = %q, want %q", in, got, want)
		}
	}
}
