#/bin/bash -e

if [ $# -ne 2 ]; then
    echo 'Usage:' $0 ' api_token solution_file'
    exit 1
fi

API_TOKEN=$1
OUTPUT=$2
TEAM_ID=178
curl --user :$API_TOKEN -X POST -H "Content-Type: application/json" \
     -d $OUTPUT https://davar.icfpcontest.org/teams/$TEAM_ID/solutions
