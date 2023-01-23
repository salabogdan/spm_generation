# SPM Generation 
 
**This project was designed to help easily migrate a project form cocoapods to swift package manager.**
### Functionalities: 
1. Based on a podspec file it will generate a swift package manifest file. 

    `spm_generation.py spm -for_project path_to_project`
2. Generate cocoapods index library
    
    `spm_generation.py generate_cocoa_index -p path_to_git_spec_repo`

### How to run the project:
1. install python 
2. install requirements from requirements.txt using `pip install -r requirements.txt`
3. Download all cocoa specs localy from the public repo using `git clone https://github.com/CocoaPods/Specs`
4. Generate the cocoapods index library file using:
      
      `spm_generation.py generate_cocoa_index -p path_on_disk_to_git_spec_repo_from_step_3` 
      
      output will be here `cocoapods/pods_index.json`
5. Generate SPM manifest file using `spm_generation.py spm -for_project path_to_project_containing_podspec_file`
6. For private cocoa pod repositories edit the `cocoapods/pods_private_index.json` file with the correct infomation
