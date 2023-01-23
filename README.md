# SPM Generation 
 
**This project was designed to help easily migrate a project form cocoapods to swift package manager.**
### Functionalities: 
1. Based on a podspec file it will generate a swift package manifest file. 

    `spm_generation.py spm -for_project path_to_project`
2. Generate cocoapods index library
    
    `spm_generation.py generate_cocoa_index -p path_to_git_spec_repo`