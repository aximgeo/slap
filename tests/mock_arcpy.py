from mock import MagicMock, patch
mock_arcpy = MagicMock()
patch.dict("sys.modules", arcpy=mock_arcpy).start()
