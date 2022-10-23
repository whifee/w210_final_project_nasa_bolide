# w210_final_project_nasa_bolide

Github space for w210 Nasa Bolide Team for Collaboration as appropriate

Addition Info contained in this Google Drive:
- https://drive.google.com/drive/u/1/folders/18IaG37JXl8x8RvfA6RKxQCcaS_O8KOOj
   
Data Descriptions of datasets:
 - `combined_df.csv`: *Used for models currently* pared down data of .2 and above confidence score (along with is_bolide tagging)
 - `full_combined_df.csv`: all data of .2 and above confidence score (along with is_bolide tagging)
 - `potential_with_vetted.csv`: this is the joined file of all the potential bolides and the vetted analyst classified bolides (and has an is_bolide field)
   - all ETL for this combining is housed in a Colab Notebook on Drive: `NASA_Bolide.ipynb`
 - `fs_file_output_bolide_pkg.csv`: this is all of the potential bolides with lat longs
   - This is a combination of the .fs files Jeff gave us from NASA. All fs file combination for this had to be done local with the `bolides` python package (that package doesn't work in cloud environments since you have to pip install -e from directly inside the repository (there are some uncommitted changes)
   - Link to the original fs files/presentations Jeff Shared: https://drive.google.com/drive/u/1/folders/1xS5gzwh7SlSBxO74McIHE7XiGzr0r63x
 - `vetted_data.csv`: these are the analyst classified bolides from the public site (`https://bolides.seti.org/`)
