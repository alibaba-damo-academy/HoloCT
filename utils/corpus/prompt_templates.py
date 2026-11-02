Caption_templates = [
            "Can you provide a caption consists of findings for this medical image?",
            "Describe the findings of the medical image you see.",
            "Please caption this medical scan with findings.",
            "What is the findings of this image?",
            "Describe this medical scan with findings.",
            "Please write a caption consists of findings for this image.",
            "Can you summarize with findings the images presented?",
            "Please caption this scan with findings.",
            "Please provide a caption consists of findings for this medical image.",
            "Can you provide a summary consists of findings of this radiograph?",
            "What are the findings presented in this medical scan?",
            "Please write a caption consists of findings for this scan.",
            "Can you provide a description consists of findings of this medical scan?",
            "Please caption this medical scan with findings.",
            "Can you provide a caption consists of findings for this medical scan?",
            "Please generate a medical report based on this image.",
            "Can you generate a diagnose report from this image.",
            "Could you analyze and provide a caption for the findings in this medical image?",
            "Please describe the observations depicted in this medical scan.",
            "Can you summarize the findings of this image in a caption?",
            "What are the significant findings in this medical image?",
            "Please provide a detailed caption outlining the findings of this image.",
            "Could you interpret and describe the findings shown in this medical scan?",
            "What conclusions can you draw from the observations in this image?",
            "Please write a descriptive caption based on the findings in this scan.",
            "What key findings can you identify from examining this medical image?",
            "Could you generate a detailed report based on the observations in this image?",
            "Can you provide a diagnosis based on the findings in this image?",
            "Please generate a comprehensive report summarizing the findings in this image.",
            "Caption the findings in this medical image?",
            "Describe the findings you see.",
            "Caption this medical scan's findings.",
            "What are the findings here?",
            "Describe these findings.",
            "Summarize the findings in these images.",
            "Caption this scan's findings.",
            "Provide a caption for this medical image's findings.",
            "Summarize the findings of this radiograph.",
            "What findings are presented in this scan?",
            "Describe this scan's findings.",
            "Generate a medical report based on this image.",
            "Can you provide a diagnosis based on this image?",
]


PosREC_templates = {
"cls_questions": [
    "Can you find the {} in this image? Give coordinates.",
    "Can you find {} in this image? Please output the coordinates.",
    "Please bounding the {} by box in this image.",
    "Where is {} in this image? Please respond with a bounding box.",
    "Where is {} in this image? Please output the box.",
    "Can you locate the {} in this image? Please output its coordinates.",
    "Could you mark the {} by bounding box in this image?",
    "Where can I find the {} in this image? Please provide its bounding box.",
    "Identify the indicated {} in this image. Please provide the coordinates of its bounding box.",
    "Can you locate the {} in this image? Please provide coordinates.",
    "Where is the {} in this image? Please output its coordinates.",
    "Please outline the {} with a bounding box in this image.",
    "Identify the location of {} in this image. Provide the bounding box coordinates.",
    "Where can I find the {} in this image? Please give its bounding box.",
    "Locate the {} in this image. Output its coordinates, please.",
    "Could you mark the {} with a bounding box in this image?",
    "Spot the {} in this image and provide its bounding box coordinates.",
    "Please pinpoint the {} in this image. Output its coordinates.",
    "Identify the {} indicated in this image. Provide coordinates for its bounding box.",
],

"des_questions": [
    "Description: {} Please answer and find it by box based on the above description.",
    "Definition: {} Please answer and show the bounding box based on the above definition.",
    "Description: {} Can you answer and find it by coordinates based on the above description.",
    "Definition: {} Please output the bounding box and answer based on the above definition.",
    "Description: {} Respond and locate it using a bounding box according to the description.",
    "Definition: {} Please provide an answer and display the bounding box according to the given definition.",
    "Description: {} Can you identify and locate it by coordinates, following the provided description or definition?",
    "Definition: {} Please output the bounding box and provide an answer based on the provided definition.",
    "Based on the description or definition, please respond to {} and indicate its location with a bounding box.",
    "{} Please answer and find it by box based on the above description.",
    "{} Please answer and show the bounding box based on the above definition.",
    "{} Can you answer and find it by coordinates based on the above description.",
    "{} Please output the bounding box and answer based on the above definition.",
    "{} Respond and locate it using a bounding box according to the description.",
    "{} Please provide an answer and display the bounding box according to the given definition.",
    "{} Can you identify and locate it by coordinates, following the provided description or definition?",
    "{} Please output the bounding box and provide an answer based on the provided definition.",
    "Please answer and find it by box based on the description. {}",
    "Please answer and show the bounding box based on the definition. {}",
    "Can you answer and find it by coordinates based on the description. {}",
    "Please output the bounding box and answer based on the definition. {}",
    "Respond and locate it using a bounding box according to the description. {}",
    "Please provide an answer and display the bounding box according to the given definition. {}",
    "Can you identify and locate it by coordinates, following the provided description or definition? {}",
    "Please output the bounding box and provide an answer based on the provided definition. {}",
    "Description: {} Find and mark it with a bounding box.",
    "Definition: {} Show the bounding box and provide the answer.",
    "Describe: {} Identify and locate it by coordinates.",
    "Define: {} Output the bounding box and respond.",
    "Description: {} Locate it with a bounding box.",
    "Definition: {} Provide the answer with the bounding box.",
    "Description: {} Identify and locate it by coordinates.",
    "Definition: {} Output the bounding box with the answer.",
    "{} Answer and locate with a bounding box.",
    "{} Show the bounding box based on the definition.",
    "{} Locate it by coordinates according to the description.",
    "{} Output the bounding box and answer.",
    "{} Respond and locate with a bounding box.",
    "{} Provide the answer with the bounding box.",
    "{} Identify and locate by coordinates.",
    "{} Output the bounding box with the answer.",
],

"cls_answers": [
    "Coordinates are {}.",
    "Sure, {}.",
    "Sure, it is {}.",
    "Sure, the bounding box is {}.",
    "{}.",
    "Here are the coordinates: {}.",
    "Of course, it's located at {}.",
    "The bounding box is given by {}.",
    "The box is {}.",
    "Coordinates: {}.",
    "{}.",
    "Yes, {}.",
    "{} are the coordinates.",
    "Sure, it's at {}.",
    "The bounding box: {}.",
    "{} - here are the coordinates.",
    "{} - it's located at these coordinates.",
    "The box: {}.",
    "Coordinates: {}.",
    "Certainly, it's at {}.",
    "Yes, it is located at {}.",
    "Sure, the bounding box: {}.",
    "It's located at {}.",
    "Here are the coordinates: {}.",
    "Of course, it's positioned at {}.",
    "The bounding box can be described by: {}.",
    "The box is specified by: {}.",
    "Yes, the coordinates are {}.",
    "Sure, it's located around {}.",
    "Yes, it's within the bounding box: {}.",
    "Absolutely, the coordinates: {}.",
    "Yes, it's within the box: {}.",
],

"des_answers": [
    "The target is {} and the coordinates is {}.",
    "The category is {} and the bounding box is {}.",
    "It is {}, {}.",
    "{}, {}",
    "The target is identified as {} and its coordinates are {}.",
    "The category is {}, the bounding box is provided as {}.",
    "It is characterized by {}, with coordinates {}.",
    "The identified attributes are {}, {}.",
    "Describing it as {}, the corresponding box is {}.",
    "The target is {} and its coordinates are {}.",
    "Categorized as {}, with a bounding box of {}.",
    "It's {}, located at {}.",
    "It's characterized as {}, with coordinates {}.",
    "Identified as {}, with a bounding box: {}.",
    "Belongs to the category of {}, with coordinates {}.",
    "Characterized by {}, with a bounding box given as {}.",
    "Describing it as {}, with coordinates {}.",
    "Identified attributes: {}, with a bounding box of {}.",
    "The category is {}, and the coordinates are {}.",
    "Describing it as {}, its bounding box is {}.",
    "It falls under the category of {}, with coordinates {}.",
],

"cls_no_answers": [
    "Sorry, there is no {}.",
    "No, we can not see {}.",
    "{} is not here.",
    "Sorry, there's no {} in sight.",
    "Unfortunately, {} is not visible here.",
    "No, {} is not present in this image.",
    "Apologies, but there's no sign of {}.",
    "We couldn't find {} in this image.",
    "It seems {} is not included in this image.",
    "Sorry, no {} found.",
    "No {} visible.",
    "Not seeing {} here.",
    "{} absent.",
    "No {} detected.",
    "Can't find {} in this image.",
],

"des_no_answers": [
    "This is {}, but not here.",
    "This is {}, however we can not see it.",
    "This is {}, but it's not present here.",
    "This is {}, but unfortunately, it's not visible in this context.",
    "While this is {}, it doesn't seem to be here.",
    "This is {}, but it's not depicted in this image.",
    "While this is {}, it's not currently observable in this scene.",
    "{} mentioned, but not here.",
    "{} described, but not visible.",
    "This is {}, but it's not here.",
    "This is {}, but it's not visible.",
    "{} mentioned, but not depicted here.",
    "{} described, but not present.",
]
}


PosREG_templates = {
"cls_questions": [
            "What target is present within the coordinates {} ?",
            "Does the bounding box {} contain any target?",
            "Within the specified region {}, what target is present?",
            "Do you know what it is in the bounding box {}?",
            "What is it in this region {}?",
            "What object is located within the coordinates {}?",
            "Within the specified area {}, what object can be found?",
            "Can you identify the object within the bounding box {}?",
            "What object is present in this region {}?",
            "What's within coordinates {}?",
            "Does the box {} contain any target?",
            "What's in the region {}?",
            "What's within the box {}?",
            "What object is in this region {}?",
            "What's located within coordinates {}?",
            "What's within the area {}?",
            "Can you identify the object within box {}?",
            "What object is present in this area {}?",
            "What target can be found within coordinates {}?",
            "Is there any target within the bounding box {}?",
            "Within the specified region {}, what target is present?",
            "Can you identify what's within the bounding box {}?",
            "What object is present in this region {}?",
            "What's located within coordinates {}?",
            "Within the specified area {}, what object can be found?",
            "Could you identify the object within the bounding box {}?",
            "What object is present in this region {}?",
            "What's located at coordinates {}?",
            "Is there a target within the box {}?",
            "What's situated in the region {}?",
            "What's inside the box {}?",
            "What object can be found in this region {}?",
            "What's situated within coordinates {}?",
            "What's within the specified area {}?",
            "Can you identify any object within box {}?",
            "What object is present in this area {}?",
        ],

"des_questions": [
            "Please describe the target and its function based on the box {} in the image.",
            "Do you know what is it in this bounding box {}? Answer and explain it.",
            "What's the target in the bounding box {}? What function does it have?",
            "What is the area marked with a box {} in the image? Can you explain it?",
            "Could you describe the object and its purpose within the bounding box {} in the image?",
            "Can you identify and describe the object within this bounding box {}? Please explain.",
            "What is the object located in the bounding box {}? Could you explain its function?",
            "Could you describe the area outlined by the box {} in the image? Please explain its significance.",
            "Describe the target and its function in box {}.",
            "What's in this box {}? Describe and explain.",
            "What's in the box {}? Explain its function.",
            "What's inside the box {}? Can you describe it?",
            "Describe the object in box {} and its purpose.",
            "Identify and describe the object in box {}. Please explain.",
            "What's the object in box {}? Describe its function.",
            "Describe the area outlined by box {} and its significance.",
            "What's in the marked area {}? Please explain.",
        ],

"cls_answers": [
            "The target is {}.",
            "Sure, the bounding box contains {}.",
            "Sure, it is {}.",
            "Sure, {} is in the bounding box.",
            "{}.",
            "The object is {}.",
            "Of course, it's {}.",
            "Certainly, {} can be found in the bounding box.",
            "Yes, the bounding box includes {}.",
            "The target is identified as {}.",
            "Affirmative, the bounding box contains {}.",
            "Yes, it is indeed {}.",
            "Yes, {} is within the bounding box.",
            "The object in question is {}.",
            "Of course, it's indeed {}.",
            "Certainly, {} can be found within the bounding box.",
            "Yes, the bounding box includes {}.",
            "Indeed, {} is present within the bounding box.",
            "Confirmed, the object is {}.",
            "Absolutely, it's {}.",
        ],

"des_answers": [
            "Sure, it is {}. {}",
            "The category is {}. {}",
            "It is {}, {}",
            "{}, {}",
            "The target is identified as {} and its description is {}",
            "The category is {}. Description: {}",
            "It is characterized by {}, {}",
            "The identified attributes are {}, {}",
            "Sure, it is {}. Describing it as {}",
            "Certainly, it is {}. {}",
            "The category is identified as {}. {}",
            "It's labeled as {}, {}",
            "Identified as {}, {}",
            "The target is recognized as {} with the following description: {}",
            "The category is {}. Here's the description: {}",
            "Characterized by {}, {}",
            "Identified attributes: {}, {}",
            "Sure, it's {}. Described as {}",
        ],

"cls_no_answers": [
    "Sorry, there is no {}.",
    "No, we can not see {}.",
    "{} is not here.",
    "Sorry, we couldn't find any {}.",
    "Nope, {} isn't visible here.",
    "{} seems to be absent.",
    "Unfortunately, {} is not present.",
    "It appears there's no {} in sight.",
    "Regrettably, we couldn't detect any {}.",
],

"des_no_answers": [
    "This is {}, but not here.",
    "This is {}, however we can not see it.",
    "This is {}, but it's not present here.",
    "This is {}, however, it's not visible in this context.",
    "The answer is {}, but it is not here.",
    "The object is {}, but it is absent in the image.",
]
}


Seg_templates = {


    "pure_seg_questions": [
        "Segment the {} in this CT scan.",
        "Please segment the {} in this CT volume.",
        "Generate a 3D mask for the {}.",
        "Provide the segmentation mask for the {}.",
        "Delineate the {} in this CT scan.",
        "Locate and segment the {}.",
    ],

    "pure_seg_answers": [
        "Here is the mask: {}.",
        "Segmentation: {}.",
        "The segmentation mask is {}.",
        "The requested segmentation is {}.",
        "Here is {}."
    ],


"unified_cls_questions": [
    "Is the {} present in this CT scan?",
    "Can you identify the {} in this CT scan?",
    "Check whether the {} is present in this CT scan.",
    "Determine whether the {} is present in this CT volume.",
    "Does this CT scan contain the {}?",
    "Can you detect the {} in this CT volume?",
    "Look for the {} in this CT scan and determine whether it is present.",
    "Assess whether the {} is visible in this CT scan.",
    "Is there evidence of the {} in this CT volume?",
    "Can the {} be found in this scan?",
],

"unified_cls_yes_answers": [
    "Yes, the {} is present in this CT scan.",
    "Yes, the {} is visible in this CT volume.",
    "Yes, the {} is detected in this scan.",
    "The {} is present in this CT scan.",
    "The {} can be identified in this CT volume.",
    "I found the {} in this scan.",
    "The scan shows the {}.",
    "There is evidence of the {} in this CT scan.",
],

"unified_cls_no_answers": [
    "No {} is visible in this CT scan.",
    "The {} is not present in this CT scan.",
    "I do not find any {} in this CT volume.",
    "The {} is absent from this scan.",
    "The {} is not detected in this CT scan.",
    "No evidence of the {} is found in this CT volume.",
    "I cannot identify the {} in this scan.",
    "There is no visible {} in this CT volume.",
],


"grounded_requests": [
    "If present, please provide its grounded mask.",
    "If found, also provide the corresponding segmentation mask.",
    "If it is present, return its 3D mask.",
    "If detected, provide its voxel-level segmentation.",
    "If visible, also ground it with a segmentation mask.",
    "If the target is present, please segment it.",
    "If identified, provide the corresponding grounded mask.",
    "If found, also delineate its spatial extent.",
    "If present, return the corresponding 3D segmentation.",
    "If detected, also provide its mask.",
],


"grounded_answers": [
    "The grounded mask is {}.",
    "Here is the corresponding mask: {}.",
    "The segmentation is {}.",
    "The corresponding 3D mask is {}.",
    "Here is its segmentation: {}.",
    "The target is grounded as {}.",
    "Its voxel-level mask is {}.",
    "The corresponding segmentation mask is {}.",
],

"unified_des_questions": [
    
    "{}. Name and segment this if present, or tell me if it's missing.",
    "{}. Identify this structure and provide the mask, or confirm if it's not found.",
    "{}. What is this? Provide its name and mask, or let me know if it's not there.",

    
    "Identify and segment the following: {}. If not in the scan, please say so.",
    "Based on this description: {}, provide the name and mask if it exists.",
    "Find the structure described as '{}'. Output its name and mask, or confirm its absence.",

    
    "In this CT, identify and mask the following: {}. If not present, let me know.",
    "Search this volume for '{}'. Provide the organ/lesion name and 3D mask if found.",
    "Based on the clinical description '{}', name and segment it, or state if it's missing."
],


"unified_des_yes_answers": [
    "This is the {}; here is its mask: {}.",
    "Identified as {}. The corresponding mask is {}.",
    "Based on the description, it's the {}; mask: {}.",
    "The structure is identified as {}; here is the 3D mask: {}.",
    "Found the {}. The volumetric segmentation is {}.",
    "It matches the {}. The output mask is {}.",
    "The clinical description refers to the {}; segmentation: {}.",
    "The identified ROI is the {}; here is the result: {}.",
    "The finding is the {}; its boundary is {}.",
    "Sure, that's the {}. The mask is {}."
],


"unified_des_no_answers": [
    "The described {} is not present in this scan.",
    "Although the text refers to the {}, it's not found in this volume.",
    "The {} cannot be identified in this specific view.",
    "No sign of the {} was found in this CT data.",
    "The scan does not contain the {} as described.",
    "The anatomical feature {} is not observable here.",
    "The description matches the {}, but it's missing from the scan.",
    "I cannot find the {} in this radiological image.",
    "No, the existence of the {} is not confirmed in this data."
],

"des_identify_only_questions": [
    "{}. What is this?",
    "{}. Identify this structure.",
    "{}. What's the name of this in the scan?",
    "{}. Tell me what this is.",
    "Based on the description '{}', what is it?",
    "Identify this: {}.",
    "What's the name of the structure matching this: {}?",
    "What anatomical feature is described as '{}'?",
    "In this CT, what is the following: {}?",
    "Name the organ or lesion matching this: {}.",
    "Identify the structure described as: {}.",
    "What is the object defined here: {}?",
    "According to the description '{}', name the ROI.",
    "What structure are we looking at here: {}?",
    "Give me the name for this: {}."
],

"des_identify_yes_answers": [
    "It's the {}.",
    "Based on the description, this is the {}.",
    "Identified as {}.",
    "The structure is the {}.",
    "This is {}.",
    "The findings match the {}.",
    "The anatomical feature is {}.",
    "That's the {}.",
    "It refers to the {}.",
    "The result is {}."
],

"blur_identify_questions": [
    "What is the blurred organ in this image?",
    "Identify the obscured structure in this scan.",
    "What's hidden behind the blur?",
    "Name the lesion that is blurred out.",
    "What anatomical part is covered by the blur?",
    "What is the name of the obscured region?",
    "Can you tell what's behind the occlusion?",
    "What is the blurred pathology here?",
    "Identify the blurred-out ROI in this CT.",
    "What's the hidden organ in this scan?",
    "Tell me what's blurred out here.",
    "What is the obscured structure shown in this volume?",
    "Identify the organ or lesion under the blur.",
    "What's the name of the part being obscured?",
    "What is the hidden finding in this image?"
],

"blur_identify_answers": [
    "It's the {}.",
    "The blurred structure is the {}.",
    "That's the {}.",
    "The hidden part is {}.",
    "It is identified as {}.",
    "The occlusion covers the {}.",
    "The obscured ROI is {}."
],

"ref_questions": [
        "Segment the region described as: \"{}\"",
        "Generate a segmentation mask for the following finding: \"{}\"",
        "Locate and segment the area corresponding to this description: \"{}\"",
        "Provide the segmentation mask for the following text: \"{}\"",
        "Identify and segment the target based on this description: \"{}\"",
        "Segment the specific pathology or anatomy described here: \"{}\"",
        "Ground the following textual description in the 3D volume: \"{}\"",
        "Find and segment the region matching this observation: \"{}\"",
        "Create a mask for the region described by: \"{}\"",
        "Segment the target corresponding to the following report excerpt: \"{}\""
    ],
    
"ref_answers": [
    "{}",
    "Segmented region: {}",
    "Target located and segmented: {}",
    "Here is the segmentation for the described finding: {}",
    "The corresponding mask is generated for: {}",
    "Segmentation mask for the requested description: {}",
    "Region identified and segmented: {}",
    "Grounding the description in the 3D volume: {}"
],


"cls_questions": [
    
    "Can you segment the {} in this image?",
    "Please provide the segmentation mask for the {} in this image.",
    "What is the segmentation for {} in this image?",
    "I need to segment the {} from this image. Can you help?",
    "Could you output the segmentation mask for the {}?",
    "Identify and segment the {} in this image, please.",
    "Show me the segment of {} in this picture.",
    "Please mask the {} in this image.",
    "Can you find and segment the {}?",
    "Segment the object labeled as {} and provide the mask.",

    
    "Can you segment the {} in this CT scan?",
    "Please provide the 3D segmentation mask for the {} in this data.",
    "I need the volumetric segmentation of the {} from this scan.",
    "In this radiological image, please segment the {}.",
    "Generate the volumetric mask for the {} shown in the CT volume.",
    "Could you provide a precise segmentation for the anatomical structure {}?",
    "Identify the boundaries of the {} in this clinical image.",
    "Please extract the {} from this CT scan and output the mask.",
    "What is the precise location of the {}? Please respond with a mask.",
    "Can you output the voxel-level segmentation for the {} in this medical volume?",

    
    "Segment the {} now.",
    "Mask the {} in this scan.",
    "Where is the {}? Give me the mask.",
    "I need to extract the {}. Provide the mask, please.",
    "Just segment the {}."
],


"cls_with_intro_questions": [
    "Can you segment the {} and provide a brief introduction to it?",
    "Please segment the {} and tell me more about it.",
    "Identify the {} in this image, provide the mask, and give a short description.",
    "Could you provide a segmentation mask for the {} along with some details?",
    "I need you to mask the {} and provide an overview of this structure.",
    "Please segment the {} and explain what we are looking at.",
    "Find the {}, output the mask, and share some background information.",
    "Segment the {} from this image and provide its description.",
    "Could you show me the {} with a mask and give me a brief summary?",
    "I'm looking for the {}. Can you mask it and provide its details?",
    "Where is the {}? Please provide the segmentation mask and an introduction.",
    "Segment and introduce the {}, please.",
    "Mask the {} and provide a brief overview.",
    "Identify, segment, and describe the {}.",
    "Give me the mask and the background information for {}.",
    "Segment the {} and provide a concise summary of its characteristics.",
    "Please provide the segmentation for {} and tell me about it.",
    "Can you find and segment the {}? Also, give me a short description.",
    "Show me the {} mask and describe it briefly.",
    "I need the mask and an introduction for the {}."
],


"des_questions": [
    
    "{}. Please identify and segment this structure.",
    "{}. What is this? Please output the name and the mask.",
    "{}. Please provide the identification and the corresponding segmentation.",
    "{}. Based on this description, segment the object and name it.",
    "{}. Can you find this in the image? Provide the name and the mask.",
    
    
    "Identify and segment the structure described as: {}.",
    "Based on the following description, provide the name and mask: {}.",
    "Please find and mask the object defined here: {}.",
    "According to this description: {}, output the identified name and segmentation.",
    "Can you identify and segment the ROI based on this: {}?",

    
    "In this scan, identify and segment the structure described as: {}.",
    "For the following CT description, output the name and the volumetric mask: {}.",
    "Please provide a precise segmentation and the name for: {}.",
    "Based on the radiological description '{}', please segment the region.",
    "Identify the anatomical structure and provide its mask: {}."
],


"cls_questions_without_seg": [
    "Is the {} present in this image?",
    "Can you find the {} in this scan?",
    "Does this image contain the {}?",
    "Is the {} visible in this view?",
    "Could you check if the {} is included in this data?",
    "Is the {} shown here?",
    "Please confirm if the {} appears in this scan.",
    "Can you identify the {} in this image?",
    "Is the {} located within this volume?",
    "Do you see the {} in this CT image?",
    "Verify the presence of the {} in this scan.",
    "Is the {} identifiable in this radiological image?",
    "Is there any sign of the {} in this view?",
    "Can you detect the {} in this CT volume?",
    "Based on the data, is the {} present?",
    "Is the anatomical feature {} observable here?",
    "Check for the {} in this medical image.",
    "Is the specified {} visible in the scan?",
    "Can you visualize the {} in this study?",
    "Confirm whether the {} is found in this image."
],


"des_questions_without_seg": [
    
    "{}. Is this present in the image?",
    "{}. Can you find this structure here?",
    "{}. Check if the described object exists in this view.",
    "{}. Is it visible in the current image?",
    "{}. Does the scan contain the object defined here?",
    "Based on this description: {}, is it present?",
    "Regarding this definition: {}, can you identify it in the image?",
    "Does this image include the following: {}?",
    "Confirm if the structure described as '{}' appears here.",
    "Can you find any sign of the object described as: {}?",

    
    "{}. Is this anatomical feature visible in the CT scan?",
    "{}. Does the described pathology appear in this volume?",
    "{}. Is this structure present across the CT slices?",
    "In this radiological data, can you find the following: {}?",
    "Based on the clinical description '{}', is it detectable?",
    "For this 3D scan, verify the existence of: {}.",
    "Check if the CT volume contains the structure described as: {}.",
    "Is the specified ROI ({}) visible in this radiological study?",
    "Does the defined structure {} appear in this cross-sectional view?",
    "Based on the medical data, is the following present: {}?"
],


"cls_yes_answers": [
    "Sure, the segmentation result is {}.",
    "The requested mask is {}.",
    "Here is the segmentation: {}.",
    "The mask for the specified structure is {}.",
    "The segmented region is {}.",
    "The target is identified as {}.",
    "The output mask for the scan is {}.",
    "The volumetric segmentation is {}.",
    "Confirmed, the structure is located at {}.",
    "The result of the analysis is {}."
],


"cls_with_intro_yes_answers": [
    "Sure. The segmented structure is the {term}. {intro}",
    "I have masked the {term} as requested. {intro}",
    "The result shows the {term}. Here is a brief introduction: {intro}",
    "Confirmed, this is the {term}. {intro}",
    "Here is the segmentation for the {term}. Regarding its details: {intro}",
    "The identified region corresponds to the {term}. {intro}",
    "I have successfully segmented the {term}. Here is some information: {intro}",
    "The mask highlights the {term}. {intro}",
    "This area represents the {term}. To provide some context, {intro}",
    "The requested {term} has been segmented. {intro}",
    "Providing the mask for the {term} along with a summary: {intro}",
    "The segmentation and analysis of the {term} are complete. {intro}",
    "The target is the {term}. Here is a short description: {intro}",
    "I've identified the {term} in the scan. For your information, {intro}",
    "The output shows the {term}. {intro}",
    "Sure, here is the {term} mask and its corresponding details: {intro}",
    "The boundary of the {term} is delineated. {intro}",
    "The requested mask for {term} is ready. {intro}",
    "This is the {term}, which can be described as follows: {intro}",
    "I have extracted the {term} for you. {intro}"
],


"des_yes_answers": [
    
    "The identified structure and its mask are {}.",
    "It is {}.",
    "The result is {}.",
    "Sure, that's the {}.",
    "Identification and segmentation: {}.",
    
    
    "Based on the description, it is {}.",
    "The object has been identified as {}.",
    "The corresponding name and mask are {}.",
    "Confirmed. The structure and its boundary are {}.",
    "The analysis reveals the structure is {}.",

    
    "The radiological finding is {}.",
    "The structure extracted from the scan is {}.",
    "The segmented anatomical region is {}.",
    "Based on the clinical data, it is {}.",
    "The identified ROI and its corresponding mask are {}."
],


"cls_yes_answers_without_seg": [
    "Yes, the {} is present.",
    "Yes, the {} can be seen in this image.",
    "Confirmed, the {} is visible.",
    "Indeed, the {} appears in this scan.",
    "Yes, the {} is identified in this view.",
    "The {} is correctly located in this image.",
    "Observation confirms that the {} is present.",
    "Yes, the {} is observable in the current data.",
    "The {} is clearly shown here.",
    "Affirmative, the {} is present in this scan.",
    "The {} is identifiable in this medical image.",
    "Yes, the structure of the {} is found here.",
    "Confirmed, the presence of the {} is verified.",
    "Yes, the {} is detectable in this study.",
    "The visual evidence confirms the {}.",
    "Yes, the {} is evident in the scan.",
    "Based on the image, the {} is present.",
    "The {} is included in this CT volume.",
    "I can confirm that the {} is present.",
    "Yes, the target {} is visible."
],


"des_yes_answers_without_seg": [
    "Yes, the {} is present.",
    "Yes, the {} is clearly visible in this image.",
    "Confirmed, the {} appears here as described.",
    "Yes, the structure identified as the {} exists in this scan.",
    "Indeed, the {} can be seen in this view.",
    "The image study confirms the presence of the {}.",
    "Yes, the {} is detectable and matches the description.",
    "Affirmative, the {} is observable in this CT volume.",
    "The finding corresponds to the {}, which is present here.",
    "Based on the description, the {} is correctly identified in this scan.",
    "Yes, we can visualize the {} in this data.",
    "Confirmed. The anatomical structure is the {} and it is visible.",
    "The visual evidence shows the {} in the scan.",
    "Yes, the specified {} is apparent in the medical image.",
    "The identification of the {} is positive."
],


"cls_no_answers_without_seg": [
    "No, the {} is not present.",
    "The {} cannot be seen in this image.",
    "The {} is not visible in this scan.",
    "There is no sign of the {} here.",
    "We cannot detect the {} in this view.",
    "The {} is not shown in this image.",
    "The {} appears to be absent from this scan.",
    "No, the {} is not identifiable in this data.",
    "The image does not contain the {}.",
    "Negative, the {} is not found.",
    "The finding is negative for the {} in this scan.",
    "The anatomical feature {} is not observable here.",
    "I do not see the {} in this view.",
    "The {} is not detectable in the provided data.",
    "No, the existence of the {} is not confirmed.",
    "The {} is missing from this radiological study.",
    "Based on the scan, the {} is not present.",
    "The structure of the {} is not shown here.",
    "There is no indication of the {} in this volume.",
    "The specified {} is not present."
],


"des_no_answers_without_seg": [
    "No, the {} is not present in this image.",
    "The {} is not visible in this scan.",
    "There is no sign of the {} here.",
    "Although the description refers to the {}, it is not found.",
    "The {} is not detectable in this specific view.",
    "The image does not contain the {} as described.",
    "Negative. The expected {} is absent from this scan.",
    "We cannot find the {} in this radiological study.",
    "The anatomical feature {} is not observable in this volume.",
    "The finding is negative for the {} in this data.",
    "While the text describes the {}, it is not captured in this image.",
    "The defined {} is missing from this CT scan.",
    "No, the existence of the {} is not confirmed in this study.",
    "The specified {} is not present in the current volume.",
    "The scan shows no evidence of the {}."
]
}


Seg_with_box_prompt_templates = {
    "cls_questions": [
        "What organ is in the coordinates {box}? Please provide its name and segmentation mask.",
        "Given the bounding box {box}, what is the target object? Provide the classification and segment.",
        "What is the object in this region {box}? I need the object name and its segmentation.",
        "Can you identify the object within the bounding box {box} and segment it?",
        "Please provide the classification and segmentation mask for the target in box {box}.",
        "Segment the target in box {box}. What is its name?",
        "Identify the target within coordinates {box} and output the segmentation mask.",
        "Based on box {box}, what is the corresponding lesion and its segmentation?",
        "Which anatomical structure is located in {box}? Segment it and state its name.",
        "What is the label for the area in {box}? Include the segment output.",
        "I need the classification and segmentation for the region {box}.",
        "What is the name of the organ within {box}? Segment it, please.",
        "Provide the identity and mask for the target indicated by {box}.",
        "What is contained in the bounding box {box}? Classification and segmentation required.",
        "Segment the object within the area {box} and tell me what it is."
    ],
    "cls_answers": [
        "The target is {cls}.",
        "It is {cls}.",
        "The object in box is {cls}.",
        "Classification and mask: {cls}.",
        "The segmentation for corresponds to {cls}.",
        "Sure, it is {cls}.",
        "The segment is {cls}.",
        "Here is {cls}.",
        "The target is identified as {cls}.",
        "The label assigned and the associated segmentation is {cls}.",
        "Category and segmentation: {cls}.",
        "It's classified with the segmentation: {cls}.",
        "The identified object is {cls}.",
        "The organ found is {cls}.",
        "Yes, {cls}."
    ],
    "des_questions": [
        "Could you describe the target in the bounding box {box}? Please give the name, description, and segmentation mask.",
        "Identify, describe, and segment the object within the region {box}.",
        "What is the name and detailed description of the lesion in {box}? Output the mask as well.",
        "Describe the object's characteristics and provide its segmentation and name, all based on the box {box}.",
        "In the coordinates {box}, what is the object? Describe it and segment it.",
        "I require the classification, description, and segmentation for the target in {box}.",
        "Please provide a comprehensive description of the organ in {box} along with its segment.",
        "Explain the features of the object within {box}. What is it and how is it segmented?",
        "Give the label, description, and segmentation mask for the structure in {box}.",
        "What is the pathological finding in {box}? State the name, description, and segmentation.",
        "Describe the anatomical structure highlighted by {box} and provide its name and segment.",
        "Provide a detailed analysis and the segmentation mask for the target in {box}.",
        "What is the object in {box}? I need a detailed description and the segmentation.",
        "Can you give the clinical description, name, and segmentation for {box}?",
        "Segment and describe the object located in {box}."
    ],
    "des_answers": [
        "The object is {cls}. Description: {des}.",
        "It is {cls}, described as {des}.",
        "Category and description: {cls}, {des}.",
        "Identified as {cls} with description: {des}.",
        "The target is {cls} and its description is {des}.",
        "The classification is {cls}. Description: {des}.",
        "The object is characterized by {cls}, {des}.",
        "The identified attributes are {cls}, {des}.",
        "Sure, it is {cls}. Describing it as {des}.",
        "The category is {cls}. Here's the description: {des}.",
        "It's labeled as {cls}, described as {des}.",
        "The target is recognized as {cls} with the following description: {des}.",
        "The lesion is {cls} and the analysis is {des}.",
        "The organ is {cls}. Description: {des}.",
        "Yes, {cls} is present, {des}."
    ],
}

Seg_and_Box_templates = {
    "cls_questions": [
        "Please locate and segment the {cls} in this image. Provide the bounding box and mask.",
        "What is the bounding box and segmentation mask for {cls}?",
        "I need the coordinates and segmentation for the {cls}.",
        "Find the {cls}. Output its bounding box and segment.",
        "Segment the {cls} and specify its bounding box.",
        "Give me the boundary coordinates and segmentation mask for the {cls}.",
        "Where is the {cls}? Provide the box and segment.",
        "Locate the {cls} and output its boundary box and segmentation mask.",
        "Could you find the bounding box and mask for the {cls} organ/lesion?",
        "Please provide the box and segmentation for {cls}.",
        "I want the bounding box for {cls}, followed by its segmentation.",
        "Identify the {cls} and provide its box and segment.",
        "Provide the bounding box and segment for the {cls} target.",
        "What are the box coordinates and segmentation for {cls}?",
        "Locate {cls} and output the box and mask."
    ],
    "cls_answers": [
        "The bounding box is {box}, and the target is {cls}.",
        "It is located at {box}, identified as {cls}.",
        "The coordinates are {box}, and the segmentation is {cls}.",
        "Box: {box}, Target: {cls}.",
        "The segmentation for {cls} is at {box}.",
        "The box is {box}. The object is {cls}.",
        "Here are the boundaries {box} for {cls}.",
        "We found {cls} at {box}.",
        "The box is {box}, and the segmented object is {cls}.",
        "The boundary is {box}, and the object is {cls}.",
        "The box is {box} for {cls}.",
        "The {cls} is bounded by {box}.",
        "The location is {box}. This is {cls}.",
        "Box {box} corresponds to {cls}.",
        "Target {cls} found at {box}."
    ],
    "cls_no_answers": [
        "Sorry, the {cls} is not present in this image.",
        "We cannot find the {cls} to provide a box and segmentation.",
        "The {cls} is not visible for localization and segmentation.",
        "Unfortunately, {cls} is absent in this image.",
        "No, we can't detect {cls}.",
        "There is no indication of {cls} here.",
        "Regrettably, {cls} cannot be observed in this image.",
        "The target {cls} is missing.",
        "I am unable to find the box and mask for {cls}.",
        "No bounding box or segmentation can be provided for {cls}.",
        "We couldn't locate the {cls} in the image.",
        "Segmentation failed; {cls} is not in the image.",
        "The requested {cls} is not available.",
        "There's no sign of {cls}.",
        "The search for {cls} yielded no results."
    ],
    "des_questions": [
        "Locate and segment the target described as '{des}'. Provide its name, bounding box, and mask.",
        "Based on the description: '{des}', what is the name, box, and segmentation mask of the object?",
        "Find the object matching the description '{des}'. Output its classification, box, and segment.",
        "I need the box and segmentation for the lesion described as '{des}'. What is its name?",
        "Please provide the classification, bounding box, and mask for the structure characterized by '{des}'.",
        "Describe the target: '{des}'. Where is it (box) and how is it segmented?",
        "Locate the object described as '{des}' and output the box and class <segment>.",
        "Segment the target matching '{des}'. What is its name and bounding box?",
        "Provide the name, boundaries, and segmentation mask for the target with the feature: '{des}'.",
        "Find the lesion with characteristics '{des}'. Provide its label, box, and segment.",
        "Identify the object by its description: '{des}'. Output the box and segmentation.",
        "Provide the detailed location (box) and segmentation for the structure '{des}'. What is its name?",
        "Locate and segment the object that fits the description: '{des}'.",
        "Find the target matching '{des}', and output its name, bounding box, and segmentation mask."
    ],
    "des_answers": [
        "The target is {cls}, located at {box}.",
        "It is {cls}, found at {box}.",
        "The object matching the description is {cls}, located at {box}.",
        "Classification: {cls}, Box: {box}.",
        "The name is {cls}, with location {box}.",
        "Found {cls} at {box}.",
        "The target is identified as {cls} at coordinates {box}.",
        "The structure matching the description is {cls}, bounded by {box}.",
        "The lesion is {cls}, found at {box}.",
        "The object is {cls}, located in {box}.",
        "It's a {cls} at {box}.",
        "The object described is {cls}, situated at {box}.",
        "The result is {cls}, located in the box {box}.",
        "The name is {cls}, located at {box}.",
        "Yes, {cls} is the target, bounded by {box}."
    ],
    "des_no_answers": [
        "This is {cls}, but it is not visible here for localization and segmentation.",
        "We recognize the object is {cls}, but it cannot be found in the image.",
        "The object matching the description is {cls}, however, it is absent in this scene.",
        "Although the target is {cls}, we are unable to provide a box or mask.",
        "The description refers to {cls}, which is not detectable in the current view.",
        "The intended target is {cls}, but we cannot locate its bounding box or segmentation.",
        "The description points to {cls}. Unfortunately, it is not present.",
        "The object to be found is {cls}, but there is no instance visible for segmentation.",
        "We have identified the subject as {cls}, but it is missing from the image.",
        "The classification is {cls}, but we cannot segment or box it here.",
        "The structure is {cls}, but it is not discernible in this particular image.",
        "The description corresponds to {cls}, which is not found at any location.",
        "Sorry, the requested {cls} is not available for boxing and segmentation.",
        "I can't provide the box and mask for the {cls} target.",
        "We cannot find the {cls} in the image to match the description."
    ]
}

Seg_with_multi_classes_templates = {
    
    "cls_questions": [
        "Can you segment {num} classes: {cls} in this image?",
        "Please segment {num} different objects: {cls}.",
        "I need segmentation masks for these {num} categories: {cls}.",
        "Segment the following {num} categories from the image: {cls}.",
        "Could you segment these: {cls}?",
        "Please provide segmentation for: {cls}.",
        "Segment objects {cls} in this image.",
        "Please segment all {num} categories: {cls} and return masks.",
        "I would like segmentation masks for: {cls}.",
        "Identify and segment the following classes: {cls}.",
        "Can you segment each of these {num} classes: {cls}?",
        "Please segment {cls} in the image and share masks.",
        "Extract segmentation masks for: {cls}.",
    ],

    
    "des_questions": [
        "Can you segment {num} classes: {cls} and describe each of them?",
        "Please segment these classes ({cls}) and give a description.",
        "I need segmentation and description for: {cls}. Descriptions.",
        "Segment the following {num} categories and explain them: {cls}.",
        "Could you segment these: {cls} and provide descriptions?",
        "Please segment and describe each of the following: {cls}.",
        "Segment these categories: {cls} and add a brief description.",
        "Identify and segment the following classes: {cls}, then give descriptions.",
        "Segment and describe each object from: {cls}.",
        "Provide segmentation masks and descriptions for: {cls}.",
    ],

    
    "cls_with_desc_single": [
        "{cls} ({des})",
        "{cls}: {des}",
        "{cls} - {des}",
        "{cls}, {des}",
        "{cls} [{des}]"
    ],

    
    "cls_no_with_desc_single": [
        "{cls} (no result, {des})",
        "{cls}: no result, {des}",
        "{cls} - no mask, {des}",
        "{cls}, not found, {des}",
        "{cls} [absent, {des}]"
    ],


    "all_yes_no_desc": [
        "All {num_yes} requested classes have been segmented: {yes_part}.",
        "Segmentation complete for all {num_yes} classes: {yes_part}.",
        "Masks for all {num_yes} classes are provided: {yes_part}.",
        "Here are segmentation results for all classes ({num_yes}): {yes_part}.",
        "All classes segmented successfully ({num_yes} total): {yes_part}."
    ],

    
    "all_yes_with_desc": [
        "All {num_yes} requested classes have been segmented with descriptions: {yes_part}.",
        "Segmentation and description complete for all {num_yes} classes: {yes_part}.",
        "Masks and descriptions for all {num_yes} classes: {yes_part}.",
        "Here are segmentation results with descriptions for all classes ({num_yes}): {yes_part}.",
    ],

    
    "some_no_no_desc": [
        "Segmentation complete for {num_yes} classes: {yes_part}, but failed for {num_no} classes: {no_part}.",
        "Masks provided for {num_yes} classes: {yes_part}. {num_no} classes could not be segmented: {no_part}.",
        "We segmented {num_yes} classes ({yes_part}) and missed {num_no} classes ({no_part}).",
        "There are masks for {num_yes} classes: {yes_part}, but no results for {num_no} classes: {no_part}."
    ],

    
    "some_no_with_desc": [
        "Segmentation with descriptions complete for {num_yes} classes: {yes_part}, but failed for {num_no} classes: {no_part}.",
        "Masks and descriptions provided for {num_yes} classes: {yes_part}. {num_no} classes could not be segmented: {no_part}.",
        "We segmented and described {num_yes} classes ({yes_part}) and missed {num_no} classes ({no_part}).",
        "There are masks & descriptions for {num_yes} classes: {yes_part}, but no results for {num_no} classes: {no_part}."
    ]
}

Radgenome_templates = {

    "Region_report_questions": [
        "Please analyze the CT scan and generate segmentation masks alongside a descriptive report. I need the findings organized in this specific flow: {region_order}.",
        "Starting with {region_order}, please segment the anatomical structures in this 3D CT volume and provide the corresponding radiology narratives for each.",
        "I'd like a detailed anatomical segmentation and a written summary for this CT study. Please process the regions according to this sequence: {region_order}.",
        "For the provided CT data, can you output both the segmentation masks and the clinical report? It’s important to follow the order of: {region_order}.",
        "Using the 3D CT volume, please perform a region-by-region segmentation and descriptive write-up, adhering to the structure: {region_order}.",
        "Could you generate the anatomical masks and report text from this CT? I need the output to follow the progression from {region_order}.",
        "Run an anatomical segmentation on this CT dataset and draft a findings report. Please ensure every part follows the requested order: {region_order}.",
        "I need the CT findings and masks delivered in a structured format. Please follow this anatomical priority: {region_order}.",
        "Map out the segmentation masks for the CT scan and write a narrative report for each segment, following the list: {region_order}.",
        "From this 3D CT, I need a combined output of segmented masks and diagnostic text. Please structure it by: {region_order}.",
        "Can you segment the following regions in the CT scan—{region_order}—and provide a clinical interpretation for each in that exact order?",
        "Generate a segment-by-segment report and mask set from this CT volume, strictly adhering to the specified sequence: {region_order}.",
        "I'm looking for a radiology report paired with segmentation masks. Please arrange the findings and masks based on: {region_order}.",
        "Process this CT study to yield anatomical segmentations and narrative descriptions, ensuring the workflow follows: {region_order}.",
        "Please extract the anatomical masks and corresponding report entries from this CT, keeping the order consistent with: {region_order}.",
        "For this CT examination, deliver a set of segmentation masks and the associated report, structured according to the list: {region_order}.",
        "I need a comprehensive analysis of the CT scan. Provide masks and report text, following the anatomical layout of {region_order}.",
        "Take the 3D CT data and generate a structured report with masks. Please stick to this sequence for the output: {region_order}.",
        "Analyze the CT volume and provide localized segmentation and text descriptions. The order of operations should be: {region_order}.",
        "Could you provide a radiology report and mask output for this CT? Please make sure the structures are addressed as: {region_order}.",
        "Using the provided CT, create a detailed map of masks and report text. The sequence of interest is {region_order}.",
        "I'd appreciate it if you could segment the CT anatomy and write the report findings, following the specific order of {region_order}.",
        "Please handle the CT segmentation and report generation. I need it organized structure-by-structure: {region_order}.",
        "Your task is to segment the CT and write a descriptive summary. Please follow the anatomical sequence: {region_order}.",
        "Can you provide masks and descriptive sentences for the anatomical regions in this CT scan? The desired order is {region_order}.",
        "Generate an anatomical segmentation for this 3D CT. The masks and report text should be presented in the order of {region_order}.",
        "For the input CT, I need a mask-based analysis and a written report. Please follow this specific path: {region_order}.",
        "Perform a region-specific analysis of this CT volume. Produce masks and text findings following: {region_order}.",
        "I need a clinical report and anatomical masks derived from this CT. Ensure the segments follow the list: {region_order}.",
        "Working with the provided CT, please output masks and findings descriptions in the following anatomical order: {region_order}.",
        "Generate both the segmentation masks and the radiology report text. Please align your output with: {region_order}.",
        "I need the CT dataset processed into anatomical masks and descriptive text. Follow this precise order: {region_order}.",
        "For the given CT, provide segmentation and matching narrative reports, structured as: {region_order}.",
        "Please produce anatomical masks and the corresponding imaging report, maintaining the sequence: {region_order}.",
        "Extract the segmentation results and write the report for this CT, following the structural sequence: {region_order}.",
        "Can you analyze the CT scan and provide masks and clinical text for each region? Please follow the sequence: {region_order}.",
        "Deliver a report and segmentation masks from the CT scan. The structures must be analyzed in this order: {region_order}.",
        "I'm requesting a mask-based segmentation and a clinical report for this CT scan, ordered by: {region_order}.",
        "Please segment the anatomy and draft the findings for this CT study, following the specified list of {region_order}.",
        "Process the 3D CT to output masks and a descriptive report, ensuring the sections follow: {region_order}."
    ]
}

RG_templates = {

  "Abd_RG": [
        "Provide a quantitative analysis of the abdominal organs, reporting volumes in cc and mean HU values.",
        "Generate a morphometric report detailing the size and density of the pancreas, spleen, liver, and kidneys.",
        "Extract the volumetric measurements and attenuation characteristics for the major abdominal organs.",
        "List the quantitative metrics (volume and mean HU) for the abdominal anatomy and summarize the impression.",
        "Report the objective CT measurements for the patient, including organ volumes and any lesion dimensions.",
        "Analyze the CT scan to provide a detailed list of organ volumes and densities, noting any enlargements.",
        "Create a data-driven report focusing on the Hounsfield Unit statistics and volumetric data of the abdomen.",
        "Identify and measure the volume and density of the liver, spleen, pancreas, and kidneys.",
        "Provide a technical assessment of the abdominal organs with precise volumetric and densitometric data.",
        "Detail the dimensions and mean attenuation values for the abdominal structures and identified lesions.",
        "Perform a quantitative volumetric assessment of the abdominal viscera and summarize the findings.",
        "Write a report containing only the objective measurements (Volume/HU) and a concluding impression.",
        "Calculate and report the size and density parameters for the pancreas, liver, spleen, and kidneys.",
        "Assess the abdominal cavity quantitatively, specifying the volume and mean HU for each major organ.",
        "Generate a structured report highlighting organ volumes, HU deviations, and lesion measurements.",
        "Provide the volumetric segmentation statistics and density analysis for the abdominal CT.",
        "Report the calculated volumes and mean attenuation values for the visceral organs.",
        "Summarize the quantitative features of the abdomen, including total kidney volume and liver lesion sizes.",
        "Present the morphometric data of the patient's abdominal organs, followed by a diagnostic impression.",
        "Detail the quantitative findings, specifically focusing on organ volumes (cc) and radiodensity (HU)."
    ],

  "Rad_RG": [
        "Generate a report following this specific system order: {ORDER_PROMPT}.",
        "Describe the findings for the following categories: {ORDER_PROMPT}.",
        "Based on the CT scan, provide a detailed evaluation for: {ORDER_PROMPT}.",
        "Please structure the radiological report using these headers: {ORDER_PROMPT}.",
        "Review the scan and report on the following areas in order: {ORDER_PROMPT}.",
        "Create a categorized report covering {ORDER_PROMPT}, detailing any abnormalities.",
        "Following the structure of {ORDER_PROMPT}, describe the patient's anatomy.",
        "Organize the findings according to this list: {ORDER_PROMPT}.",
        "Provide a section-by-section analysis for {ORDER_PROMPT}.",
        "Using {ORDER_PROMPT} as the outline, generate a full medical report."
        "Generate a comprehensive CT report categorized by organ system.",
        "Provide a full radiological review of the patient, organized by anatomical sections.",
        "Evaluate the scan and report findings for the Abdomen, Bone, Lungs, and Mediastinum separately.",
        "Create a multi-system report detailing the findings in the chest and abdomen.",
        "Write a detailed diagnostic report separated into distinct anatomical categories.",
        "Assess the patient's condition system-by-system, noting any pathological findings.",
        "Produce a structured report with headers for each major organ system evaluated.",
        "Describe the radiological findings, organizing the text by anatomical regions.",
        "Summarize the CT findings, strictly categorizing the description by organ system.",
        "Provide a systematic evaluation of the scan, covering all visible anatomical structures.",
    ],

  "Mer_stru_RG": [
        "Follow this anatomical checklist to generate the report: {ORDER_PROMPT}.",
        "Write the report by evaluating the structures in this order: {ORDER_PROMPT}.",
        "Please describe the findings sequentially for: {ORDER_PROMPT}.",
        "Using the following flow: {ORDER_PROMPT}, assess the patient's scan.",
        "Structure the clinical findings according to this sequence: {ORDER_PROMPT}.",
        "Report on the patient's condition by stepping through {ORDER_PROMPT}.",
        "Adhering to the order {ORDER_PROMPT}, provide a detailed CT assessment.",
        "Generate a report that specifically addresses {ORDER_PROMPT} in that order.",
        "Review the anatomy following the path: {ORDER_PROMPT}.",
        "Create a finding-by-finding report based on this list: {ORDER_PROMPT}."
        "Write a standard clinical report following the fixed anatomical order.",
        "Generate a diagnostic report evaluating the abdominal and pelvic organs sequentially.",
        "Perform a standard review of the CT scan from the lower thorax down to the musculoskeletal system.",
        "Assess the scan and report findings in the standard clinical sequence.",
        "Provide a routine abdominal CT report, checking all organs in the usual anatomical order.",
        "Create a clinical report detailing findings from the liver, biliary system, and GI tract downwards.",
        "Evaluate the internal organs sequentially and report any interval changes or abnormalities.",
        "Write a full report covering the abdomen and pelvis in the standard radiological order.",
        "Describe the findings for the abdominal organs, vasculature, and nodes in the correct sequence.",
        "Generate a systematic clinical report including negative findings and prior comparisons.",
    ],

  "Mer_narr_RG": [
        "Generate a narrative radiological report organized by major anatomical regions.",
        "Provide a descriptive assessment of the patient's anatomy, grouped by body blocks.",
        "Write a CT report using paragraph-based descriptions for each major anatomical section.",
        "Assess the scan and provide a continuous narrative for each identified regional block.",
        "Create a diagnostic summary that aggregates findings into broad anatomical categories.",
        "Produce a radiological report using cohesive paragraphs to describe the findings in each body region.",
        "Evaluate the CT scan and organize the findings into narrative blocks from top to bottom.",
        "Describe the findings for the solid organs and vasculature within their respective anatomical sections.",
        "Write a comprehensive assessment of the scan, grouping findings by major body segments.",
        "Draft a clinical report that summarizes the findings in full sentences within regional paragraphs.",
        "Generate a structured report that moves through the major anatomical regions in a narrative sequence.",
        "Provide a detailed review of the scan, using narrative summaries for the chest, abdomen, and pelvis as visualized.",
        "Summarize the radiological findings by body region, focusing on a narrative flow rather than an organ list.",
        "Create a report that describes all visible structures within their broader anatomical context.",
        "Evaluate the patient's condition by providing a descriptive summary for each major section of the scan.",
        "Produce a clinical report detailing findings for all relevant anatomical zones in paragraph format.",
        "Assess the CT images and provide a cohesive narrative for each identified anatomical segment.",
        "Generate a report that groups multiple physiological systems into unified regional blocks.",
        "Describe the internal anatomy and any pathological findings using a regional block-style format.",
        "Write a diagnostic report that transitions through the body regions, providing a full narrative for each."
    ],

    "AMOS-MM_region": [
        "{tag} Provide a descriptive report of the `{region}`.",
        "{tag} Describe the radiological appearance of the `{region}` in detail.",
        "{tag} What are the findings for the `{region}` as visualized in this scan?",
        "{tag} Evaluate the `{region}` and provide a detailed assessment.",
        "{tag} Describe any observations regarding the organs and tissues in the `{region}`.",
        "{tag} Generate a complete findings section for the `{region}`.",
        "{tag} Outline the characteristics of the `{region}` based on the current imaging.",
        "{tag} Give a full radiological account of the `{region}`.",
        "{tag} Examine the `{region}` and describe its morphology and density.",
        "{tag} What is the radiological status of the `{region}`? Provide a narrative summary."
    ],

    "Merlin_region": [
        "{tag} Assess the `{region}` and state the findings.",
        "{tag} What is the radiological status of the `{region}`?",
        "{tag} Report on the condition of the `{region}`.",
        "{tag} Identify any significant findings in the `{region}`.",
        "{tag} What does the scan show for the `{region}`?",
        "{tag} Provide a concise assessment of the `{region}`.",
        "{tag} Document the findings for the `{region}`.",
        "{tag} Evaluate the status of the `{region}`.",
        "{tag} Are there any notable observations in the `{region}`?",
        "{tag} State the imaging findings for the `{region}`."
    ],

    "Radgenome_region": [
        "{tag} Examine the `{region}` and describe its structural findings.",
        "{tag} Analyze the `{region}` for any pathological or anatomical changes.",
        "{tag} Provide an evaluation of the `{region}`'s appearance.",
        "{tag} Describe the integrity and status of the `{region}`.",
        "{tag} What are the observations regarding the `{region}` in this study?",
        "{tag} Evaluate the `{region}` and report on its components.",
        "{tag} Characterize the visualized `{region}` based on the scan.",
        "{tag} Note the radiological features of the `{region}`.",
        "{tag} Provide a structural assessment of the `{region}`.",
        "{tag} What is revealed during the examination of the `{region}`?"
    ],

    "FLARE-2025_region": [
        "{tag} Evaluate the `{region}` for any evidence of abnormality.",
        "{tag} Describe the status of the `{region}` regarding its size, morphology, or density.",
        "{tag} Are there any significant or abnormal findings in the `{region}`?",
        "{tag} Assess the `{region}` and report on the observed findings.",
        "{tag} Describe the appearance of the `{region}` in this CT volume.",
        "{tag} Provide the findings for the `{region}`, noting any pathological or normal features.",
        "{tag} Examine the `{region}` and state whether any lesions or issues are present.",
        "{tag} What is the radiological status of the structures within the `{region}`?",
        "{tag} Report on the `{region}`'s morphology and any identifying characteristics.",
        "{tag} Summarize the imaging observations for the `{region}`."
    ],

    "AMOS-MM_all": [
        "{tag} Provide a comprehensive radiological narrative for the following regions: {region_list}.",
        "{tag} Generate a detailed findings report covering the {region_list}, detailing morphology and any lesions found.",
        "{tag} Describe the radiological appearance across the {region_list} in a continuous, structured format.",
        "{tag} What are the detailed clinical observations for the organs and tissues in the {region_list}?",
        "{tag} Deliver a full account of the findings for the following anatomical areas: {region_list}.",
        "{tag} Provide an in-depth assessment of the {region_list}, focusing on organ size, shape, and parenchymal density.",
        "{tag} Write a structured findings section for the 3D CT scan, including {region_list}.",
        "{tag} Outline the visual characteristics and enhancement patterns observed in the {region_list}.",
        "{tag} Based on this scan, provide a systematic description of findings within the {region_list}.",
        "{tag} Construct a detailed report summarizing the status of the {region_list} as captured in this volume."
    ],

    "Merlin_all": [
        "{tag} Assess the radiological status of the following: {region_list}.",
        "{tag} Provide a concise clinical summary of findings for the {region_list}.",
        "{tag} What is the condition of the following anatomical structures: {region_list}?",
        "{tag} Report the imaging observations for the {region_list} in a systematic manner.",
        "{tag} Summarize the status of the {region_list}, noting any significant abnormalities or normal findings.",
        "{tag} Document the clinical status for each of the following areas: {region_list}.",
        "{tag} Provide a structured overview of the scan findings for the {region_list}.",
        "{tag} Identify and state any notable findings within the {region_list}.",
        "{tag} What does the 3D CT study reveal regarding the {region_list}?",
        "{tag} Give a brief and professional assessment of the following regions: {region_list}."
    ],

    "Radgenome_all": [
        "{tag} Conduct a structural evaluation of the {region_list} based on the CT imaging data.",
        "{tag} Report the anatomical findings for the following regions: {region_list}.",
        "{tag} Analyze the {region_list} for any pathological, structural, or sequelae changes.",
        "{tag} Provide a technical description of the status and integrity of the {region_list}.",
        "{tag} What are the observations regarding the contours and dimensions of the {region_list}?",
        "{tag} Evaluate the components of the {region_list} as visualized in this study.",
        "{tag} Characterize the anatomical appearance of the {region_list} in this scan.",
        "{tag} Detail the findings for the {region_list}, focusing on their internal structures and boundaries.",
        "{tag} Provide a systematic assessment of the {region_list} in the specified imaging windows.",
        "{tag} What is the radiological interpretation for the following anatomical sections: {region_list}?"
    ],

    "FLARE-2025_all": [
        "{tag} Systematically evaluate the following systems and regions for any evidence of abnormality: {region_list}.",
        "{tag} Provide a structured report assessing the morphology and density of the {region_list}.",
        "{tag} Are there any significant findings in the following areas: {region_list}? Please describe.",
        "{tag} Report on the status of the {region_list}, noting any pathological or normal features identified.",
        "{tag} Describe the appearance of the {region_list} focusing on size, morphology, and regularity.",
        "{tag} Summarize the imaging observations for the following anatomical groups: {region_list}.",
        "{tag} Examine the {region_list} and state the findings for each system.",
        "{tag} Provide the findings for the structures within the {region_list} regarding their parenchymal integrity.",
        "{tag} Check for abnormalities in the {region_list} and provide a standardized findings report.",
        "{tag} Document the radiological status of the {region_list} in this CT volume."
    ],

    "INSPECT_RG": [
        "Generate a numbered radiological impression for this CT scan.",
        "Write the diagnostic impression for this CTPA as a numbered list.",
        "Evaluate the scan for pulmonary embolism and list all findings in a numbered impression.",
        "Provide a structured, numbered clinical impression based on this CT volume.",
        "Summarize the CTPA findings into a formal, numbered impression.",
        "Generate the final IMPRESSION section for this scan in a standard numbered format.",
        "Detail the PE status and any incidental findings in a numbered impression.",
        "Write a concise, numbered diagnostic summary for this chest CT.",
        "Formulate the clinical impression for this scan as a numbered list.",
        "Provide the final radiological impression, noting all findings in numerical order.",
        "Assess the CT volume and generate a numbered list of diagnostic impressions.",
        "Summarize all primary and incidental findings into a numbered CTPA impression.",
        "Draft the IMPRESSION section, listing all radiological findings systematically.",
        "Generate a comprehensive, numbered impression for this thoracic CT.",
        "Provide a standard numbered impression evaluating the pulmonary vasculature and secondary findings.",
        "List the diagnostic conclusions for this CTPA in a numbered impression format.",
        "Write the final numbered impression, including any clinical recommendations or summaries.",
        "Evaluate this 3D CT and summarize the impression in a numbered list.",
        "Provide a formal, numbered summary of all relevant findings in this scan.",
        "Generate the clinical impression, systematically listing all thoracic and abdominal findings."
    ],


    "BIMCV_RG": [
        "Generate a radiology report for this CT scan.",
        "Please write a radiology report for the given CT volume.",
        "Describe the radiological findings in this 3D CT scan.",
        "Provide a concise radiology report for this CT volume.",
        "Generate a clinical imaging report based on the given 3D CT scan.",
    ]
}


VQA_templates = {


    "std_mcq": [ 
        {"question": "{q}\n{opts}\nAnswer with the full option.", "answer": "{ans}"},
        {"question": "Based on the CT scan, {q}\n{opts}\nAnswer:", "answer": "{ans}"},
        {"question": "Question: {q}\nOptions:\n{opts}\nSelect the correct option.", "answer": "{ans}"},
        {"question": "Looking at this medical image, which of the following is correct?\n{q}\n{opts}", "answer": "{ans}"},
        {"question": "{q}\n{opts}", "answer": "{ans}"}
    ],
    "reasoning_mcq": [ 
        {"question": "{q}\n{opts}\nSelect the answer and provide your reasoning based on the scan.", "answer": "{ans}. {reason}"},
        {"question": "{q}\n{opts}\nExplain the logic behind your choice.", "answer": "{ans}. {reason}"},
        {"question": "Question: {q}\nOptions:\n{opts}\nAnswer with explanation.", "answer": "{ans}. {reason}"},
        {"question": "Based on the findings in the imaging, {q}\n{opts}\nGive the answer and the reason.", "answer": "{ans}. {reason}"},
        {"question": "Analyze the CT image and answer: {q}\n{opts}", "answer": "{ans}. {reason}"}
    ],
    "binary": [ 
        {"question": "{q} (Yes/No)", "answer": "{ans}"},
        {"question": "Based on the medical image, {q}? Yes or No?", "answer": "{ans}"},
        
        {"question": "Please answer with Yes or No: {q}", "answer": "{ans}"},
        {"question": "True or False: {q}", "answer": "{ans_tf}"}
    ],
    "open_ended": [ 
        {"question": "{q}", "answer": "{ans}"},
        {"question": "Question: {q}\nAnswer:", "answer": "{ans}"},
        {"question": "Based on the CT volume, {q}", "answer": "{ans}"},
        {"question": "Look at the 3D CT scan and answer: {q}", "answer": "{ans}"},
        {"question": "According to the 3D scan, {q}", "answer": "{ans}"}
    ]
}


Grounded_VQA_templates = {
    "questions": [
        "Ground your answer with the mask.",
        "Provide the grounded mask.",
        "Include the grounded mask.",
        "Give the grounded mask.",
        "Also provide the grounded mask.",
        "Please provide the grounded mask.",
        "Please include the grounded mask.",
        "Please give the grounded mask.",
        "Ground the answer with the mask.",
        "Ground your response with the mask.",
        "Provide the corresponding grounded mask.",
        "Include the corresponding grounded mask.",
        "Please respond with the grounded mask.",
        "Please also provide the grounded mask.",
        "Please ground your answer with the mask.",
        "Provide a segmentation mask to ground your answer.",
        "Include a segmentation mask to ground your answer.",
        "Please provide a segmentation mask to ground your answer.",
        "Please accompany your answer with the grounded mask.",
        "Please accompany your response with the grounded mask."
    ],

    "answer_single": [
        "{grounded} is the grounded mask.",
        "{grounded} is the corresponding mask.",
        "{grounded} is the grounding mask.",
        "{grounded} is the corresponding grounded mask.",
        "The grounded mask is {grounded}.",
        "The corresponding mask is {grounded}.",
        "Grounded mask: {grounded}.",
        "Grounding: {grounded}."
    ],

    "answer_multiple": [
        "{grounded} are the grounded masks.",
        "{grounded} are the corresponding masks.",
        "{grounded} are the grounding masks.",
        "{grounded} are the corresponding grounded masks.",
        "The grounded masks are {grounded}.",
        "The corresponding masks are {grounded}.",
        "Grounded masks: {grounded}.",
        "Grounding: {grounded}."
    ]
}


Seg_templates["unified_cls_grounded_questions"] = [
    f"{question} {request}"
    for question in Seg_templates["unified_cls_questions"]
    for request in Seg_templates["grounded_requests"]
]

Seg_templates["unified_cls_grounded_yes_answers"] = [
    f"{answer.replace('{}', '{0}')} {grounded_answer.replace('{}', '{1}')}"
    for answer in Seg_templates["unified_cls_yes_answers"]
    for grounded_answer in Seg_templates["grounded_answers"]
]

Seg_templates["unified_cls_grounded_no_answers"] = (
    Seg_templates["unified_cls_no_answers"]
)