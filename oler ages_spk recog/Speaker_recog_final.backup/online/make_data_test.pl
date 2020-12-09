#!/usr/bin/perl
#
# Copyright 2018  Ewald Enzinger
#           2019  Minsoo Kim
#
# Usage: make_voxceleb2.pl /export/voxceleb2 dev data/dev
#

if (@ARGV != 2) {
  print STDERR "Usage: $0 <path> <path-to-data-dir>\n";
  print STDERR "e.g. $0 /export/dataset data/dev\n";
  exit(1);
}

($data_base, $out_dir) = @ARGV;

opendir my $dh, "$data_base/test" or die "Cannot open directory: $!";
opendir my $dh2, "$data_base/train" or die "Cannot open directory: $!";
my @spkr_dirs = grep {-d "$data_base/train/$_" && ! /^\.{1,2}$/} readdir($dh2);
closedir $dh;
closedir $dh2;

if (system("mkdir -p $out_dir") != 0) {
  die "Error making directory $out_dir";
}

open(SPKR, ">", "$out_dir/utt2spk") or die "Could not open the output file $out_dir/utt2spk";
open(WAV, ">", "$out_dir/wav.scp") or die "Could not open the output file $out_dir/wav.scp";
open(TRIALS, ">", "$out_dir/trials") or die "Could not open the output file $out_dir/trials";

opendir my $dh, "$data_base/test/" or die "Cannot open directory: $!";  
my @files = map{s/\.[^.]+$//;$_}grep {/\.wav$/} readdir($dh);
closedir $dh;
foreach (@files) {
  my $name = $_;
  my $wav = "$data_base/test/$name.wav";
  my $utt_id = "$name";
  print WAV "$utt_id", " $wav", "\n";
  print SPKR "$utt_id", " test", "\n";
  foreach (@spkr_dirs) {
    my $spkr_id = $_;
    if ( $spkr_id eq "test") {
    }else {
      print TRIALS "$spkr_id", " $name", "\n";
    }
  }
}
close(TRIALS) or die;
close(SPKR) or die;
close(WAV) or die;



if (system(
  "utils/utt2spk_to_spk2utt.pl $out_dir/utt2spk >$out_dir/spk2utt") != 0) {
  die "Error creating spk2utt file in directory $out_dir";
}
system("env LC_COLLATE=C utils/fix_data_dir.sh $out_dir");
if (system("env LC_COLLATE=C utils/validate_data_dir.sh --no-text --no-feats $out_dir") != 0) {
  die "Error validating directory $out_dir";
}
