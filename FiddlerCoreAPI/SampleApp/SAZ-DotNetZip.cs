#if SAZ_SUPPORT
using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using Ionic.Zip;
using System.Diagnostics;

namespace Fiddler
{
    class DNZSAZProvider : ISAZProvider
    {
        // This is Func<String> but we don't have that in .NET2.0
        public delegate string ObtainPasswordDelegate();

        public static ObtainPasswordDelegate fnObtainPwd
        {
            get;
            set;
        }

        public ISAZWriter CreateSAZ(string sFilename)
        {
            return new DNZSAZWriter(sFilename);
        }

        public ISAZReader LoadSAZ(string sFilename)
        {
            return new DNZSAZReader(sFilename);
        }

        public bool BufferLocally
        {
            get
            {
                return false;
            }
        }

        public bool SupportsEncryption
        {
            get
            {
                return true;
            }
        }
    }

    class DNZSAZReader : ISAZReader
    {
        private ZipFile _oZip;
        private string _sFilename;

        private string _sPassword;

        public string Filename
        {
            get
            {
                return _sFilename;
            }
        }

        public void Close()
        {
            _oZip.Dispose();
            _oZip = null;
        }

        public string Comment
        {
            get
            {
                return _oZip.Comment;
            }
        }

        string _EncryptionMethod;
        public string EncryptionMethod
        {
            get
            {
                return _EncryptionMethod;
            }
        }

        string _EncryptionStrength;
        public string EncryptionStrength
        {
            get
            {
                return _EncryptionStrength;
            }
        }

        private bool PromptForPassword()
        {
            DNZSAZProvider.ObtainPasswordDelegate fnGetPwd = DNZSAZProvider.fnObtainPwd;

            if (null == fnGetPwd) return false;
            _sPassword = fnGetPwd.Invoke();

            if (!String.IsNullOrEmpty(_sPassword))
            {
                _oZip.Password = _sPassword;
                return true;
            }

            return false;
        }

        public Stream GetFileStream(string sFilename)
        {
            ZipEntry oZE = _oZip[sFilename];
            if (null == oZE)
            {
                return null;
            }

            if ((oZE.UsesEncryption) && String.IsNullOrEmpty(_sPassword))
            {
                StoreEncryptionInfo(oZE.Encryption);
                if (!PromptForPassword()) { throw new OperationCanceledException("Password required."); }
            }

            Stream strmResult = null;

        RetryWithPassword:
            try
            {
                strmResult = oZE.OpenReader();
            }
            catch (Ionic.Zip.BadPasswordException)
            {
                if (!PromptForPassword()) { throw new OperationCanceledException("Password required."); }
                goto RetryWithPassword;
            }
            catch (Exception eX)
            {
                Debug.Assert(false, eX.Message);
                FiddlerApplication.ReportException(eX, "Error saving SAZ");
            }

            return strmResult;
        }

        private void StoreEncryptionInfo(EncryptionAlgorithm oEA)
        {
            switch (oEA)
            {
                case EncryptionAlgorithm.PkzipWeak:
                    _EncryptionMethod = "PKZip";
                    _EncryptionStrength = "56"; // Is that right?
                    break;
                case EncryptionAlgorithm.WinZipAes128:
                    _EncryptionMethod = "WinZipAes";
                    _EncryptionStrength = "128";
                    break;
                case EncryptionAlgorithm.WinZipAes256:
                    _EncryptionMethod = "WinZipAes";
                    _EncryptionStrength = "256";
                    break;
                default:
                    Debug.Assert(false, "Unknown encryption algorithm");
                    _EncryptionMethod = "Unknown";
                    _EncryptionStrength = "0";
                    break;
            }
        }

        public byte[] GetFileBytes(string sFilename)
        {
            Stream strmBytes = this.GetFileStream(sFilename);
            if (strmBytes == null) return null;

            byte[] arrData = Utilities.ReadEntireStream(strmBytes);
            strmBytes.Close();
            return arrData;
        }

        public string[] GetRequestFileList()
        {
            List<string> listFiles = new List<string>();

            // TODO: Use (faster?) _oZip.SelectEntries method instead
            foreach (ZipEntry oZE in _oZip)
            {
                if (!oZE.FileName.EndsWith("_c.txt", StringComparison.OrdinalIgnoreCase) || !oZE.FileName.StartsWith("raw/", StringComparison.OrdinalIgnoreCase))
                {
                    // Not a request. Skip it.
                    continue;
                }

                listFiles.Add(oZE.FileName);
            }

            return listFiles.ToArray();
        }

        internal DNZSAZReader(string sFilename)
        {
            _sFilename = sFilename;
            _oZip = new ZipFile(sFilename);
            foreach (string s in _oZip.EntryFileNames)
            {
                Trace.WriteLine(s);

            }
            /*if (!_oZip.EntryFileNames.Contains("raw/"))
            {
                throw new Exception("The selected file is not a Fiddler-generated .SAZ archive of Web Sessions.");
            }*/
        }
    }

    class DNZSAZWriter : ISAZWriter
    {
        private ZipFile _oZip;
        private string _sFilename;

        internal DNZSAZWriter(string sFilename)
        {
            _sFilename = sFilename;
            _oZip = new ZipFile(sFilename);

            // We may need to use Zip64 format if the user saves more than 21844 sessions, because
            // each session writes 3 files and the non-Zip64 format is limited to 65535 files.
            _oZip.UseZip64WhenSaving = Zip64Option.AsNecessary;

            // Create the directory explicitly (not strictly required) because this matches
            // legacy behavior and some code checks for it.
            _oZip.AddDirectoryByName("raw");
        }

        private string _EncryptionMethod;
        public string EncryptionMethod
        {
            get
            {
                if (String.IsNullOrEmpty(_EncryptionMethod)) StoreEncryptionInfo(_oZip.Encryption);
                return _EncryptionMethod;
            }
        }

        private void StoreEncryptionInfo(EncryptionAlgorithm oEA)
        {
            switch (oEA)
            {
                case EncryptionAlgorithm.PkzipWeak:
                    _EncryptionMethod = "PKZip";
                    _EncryptionStrength = "56"; // Is that right?
                    break;
                case EncryptionAlgorithm.WinZipAes128:
                    _EncryptionMethod = "WinZipAes";
                    _EncryptionStrength = "128";
                    break;
                case EncryptionAlgorithm.WinZipAes256:
                    _EncryptionMethod = "WinZipAes";
                    _EncryptionStrength = "256";
                    break;
                default:
                    Debug.Assert(false, "Unknown encryption algorithm");
                    _EncryptionMethod = "Unknown";
                    _EncryptionStrength = "0";
                    break;
            }
        }

        private string _EncryptionStrength;
        public string EncryptionStrength
        {
            get
            {
                if (String.IsNullOrEmpty(_EncryptionStrength)) StoreEncryptionInfo(_oZip.Encryption);
                return _EncryptionStrength;
            }
        }

        public void AddFile(string sFilename, SAZWriterDelegate oSWD)
        {
            Ionic.Zip.WriteDelegate oWD = (sFN, oS) =>
            {
                oSWD.Invoke(oS);
            };
            _oZip.AddEntry(sFilename, oWD );
        }

        /// <summary>
        /// Writes the ContentTypes XML to the ZIP so Packaging APIs can read it.
        /// See http://en.wikipedia.org/wiki/Open_Packaging_Conventions
        /// </summary>
        /// <param name="odfZip"></param>
        private void WriteODCXML()
        {
            const string oPFContentTypeXML =
               "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\r\n<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">\r\n" +
               "<Default Extension=\"htm\" ContentType=\"text/html\" />\r\n<Default Extension=\"xml\" ContentType=\"application/xml\" />\r\n<Default Extension=\"txt\" ContentType=\"text/plain\" />\r\n</Types>";

            _oZip.AddEntry("[Content_Types].xml", new WriteDelegate(delegate(string sn, Stream strmToWrite)
                {
                byte[] arrODCXML = Encoding.UTF8.GetBytes(oPFContentTypeXML);
                    strmToWrite.Write(arrODCXML, 0, arrODCXML.Length);
                }));
        }

        public bool CompleteArchive()
        {
            WriteODCXML();
            _oZip.Save();
            _oZip = null;

            return true;
        }

        public string Filename
        {
            get { return _sFilename; }
        }

        public string Comment
        {
            get
            {
                return _oZip.Comment;
            }
            set
            {
                _oZip.Comment = value;
            }
        }

        public bool SetPassword(string sPassword)
        {
#region PasswordProtectIfNeeded
            if (!String.IsNullOrEmpty(sPassword))
            {
                if (CONFIG.bUseAESForSAZ)
                {
                    if (FiddlerApplication.Prefs.GetBoolPref("fiddler.saz.AES.Use256Bit", false))
                    {
                        _oZip.Encryption = EncryptionAlgorithm.WinZipAes256;
                    }
                    else
                    {
                        _oZip.Encryption = EncryptionAlgorithm.WinZipAes128;
                    }
                }
                _oZip.Password = sPassword;
            }
#endregion PasswordProtectIfNeeded

            return true;
        }
    }
}
#endif