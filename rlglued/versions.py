#
#  $Revision: 738 $
#  $Date: 2009-02-12 17:32:12 -0500 (Thu, 12 Feb 2009) $
#  $Author: brian@tannerpages.com $
#  $HeadURL: http://rl-glue-ext.googlecode.com/svn/trunk/projects/codecs/Python/src/rlglue/versions.py $


def get_svn_codec_version():
    svn_glue_version = "$Revision: 738 $"
    just_the_number = svn_glue_version[11:len(svn_glue_version) - 2]
    return just_the_number


def get_codec_version():
    return "2.1"
