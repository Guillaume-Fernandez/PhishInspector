forms=`cat $1 | awk '/<form/{flag=1} flag; /<\/form/{flag=0}' `
param=""
for form in $forms
do
  if [[ $form == *"name="* ]]
  then
    name=`echo $form|awk -F "name=\"" '{print $2}'|awk -F "\"" '{print $1}'`
    # echo $name
    param=$param$name"=param&"
  fi
  if [[ $form == *"action="* ]]
  then
    if [[ $form == *'action="/'* ]] #When action="/..." -> action=...
    then
      form=$(echo $form | sed 's|/||')
    fi
    url=`echo $form|awk -F "action=\"" '{print $2}'|awk -F "\"" '{print $1}'`
    # echo $url
  fi
  if [[ $form == *"</form"* ]]
  then
    request="curl -d \""${param%?}"\" -X POST http://localhost:80/"${url[$i]}
    echo $request
    $request
    param=""
  fi
done
