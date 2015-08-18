# User Manual #

This is the user manual for users to understand the proper usage of Shredder.


# Purpose of Shredder #

Shredder is a GUI frontend made to simplify the use of the GNU Coreutil's "shred" command found in most Linux OS. Typing "shred ..." command to shred files in the terminal is a tedious work especially if you are going to shred many files or folders. Shredder provides a simple GUI interface for users to shred their folders and files without the hassle of repeatedly attempting to shred each file via the terminal command. Shredder also makes it user-friendly and less frightening for new users of the Linux platform and makes the secure deletion of files and folders more easily accessible. This would allow more users to become comfortable with securely sanitizing their filesystem so that in an event the computer falls into the wrong hands, sensitive data would have been securely erased from the filesystem which could no longer be forensically retrieved.


# The GUI interface controls #

The top most row contains a textbox where you fill in the path to the files or folders you may want to delete. There are three buttons next to the textbox. The button closest to the textbox is for users to select a file to shred. The other buttons are for users to select a folder to shred all of it's contents and finally the last button at the far right corner is for the selection of the trash bin to shred trash bin contents. You may drag and drop a file or a folder into the textbox as well.

The next level is to specify details on how the shredding should work. The "shred iterations" define how many times a file should be overwritten to cover it's bytes on the storage media. The more iterations you specify, the more securely shredded the file would be. The issue with higher shredding iterations meant that the slower and more wear and tear your storage media would have to bear. The recommended amount would vary according to how confidential and secretive the file you want to shred. For day-to-day usage, a minimum of 5 iteration would suffice.

The 'zero-ing' option could be enabled or disabled via a checkbox which you would tick inside to select it (to enable or disable). The zero-ing function would simply overwrite all the bytes on the segment of your storage media containing the file(s) to '0' bits (which zero bits meant that no data is there).

The 'remove' option next to the 'zero-ing' option allows users to delete files and folders that have been shredded to ensure files or folders that remain although their contents have been shredded would be deleted out of the filesystem. This is simply a safety measure to control if you would want to delete a shredded file or folder if it continues to exist after the shredding operation.

Finally, the bottom right button allows you to begin the shred operation.


# What Shredder CANNOT Do #

  * Shredder does not provide the flexibility and full features of the command line 'shred' function.

  * Shredder does not provide some indicators on the exact progress of the shredding as there are no functions provided by the 'shred' command to do so.

# WARNING #

  * Some laws in certain countries requires the retention of digital artifacts for a set number of years. Data-retention laws (e.g. Sarbanes-Oxley act) would require corporations to retain data for a set amount of time to allow retrieval and audit to take place. Please use Shredder (especially for corporates and organisations) wisely.

  * Shredding files would definitely bring some minor stress on the storage media as you are overwriting data over a certain segment of your media repetitively at a more frequent rate. It should not be of any major concern unless you are overwriting a segment of a storage media for more than a million iterations or so.

  * Shredding has been found to be rather ineffective for sanitizing flash-based storage media (thumbdrives, flash drives, SD cards, flash chip devices ...). To understand more on why shredding would work pretty poorly on flash drives, please read http://www.schneier.com/blog/archives/2011/03/erasing_data_fr.html. The best way to destroy a flash based devices is to physically destroy the flash memory chips.

  * Shredding temp files are not in the current list of features.