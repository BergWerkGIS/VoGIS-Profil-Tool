# -*- coding: iso-8859-15 -*-

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bergw
#
# Copyright:   (c) bergw 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import collections #ordereddic



class ProfileHelper:


	def __init__(
		self
		, profiles
		):

		self.Profiles=profiles


	def ProfileCount(self):
		return len(self.Profiles)



	def AttributeCount(self, profileNumber):
		if len(self.Profiles[profileNumber])<5:
			return 0
		else:
			return len(self.Profiles[profileNumber][4])



	def RasterCount(self, profileNumber):
		return len(self.Profiles[profileNumber][2][0])



	def GetPoints(self, profileNumber):
		return self.Profiles[profileNumber][0]



	def GetAttributes(self, profileNumber):
		return self.Profiles[profileNumber][4]



	def GetDistances(self, profileNumber):
		return self.Profiles[profileNumber][1]



	def GetRasterVals(self, profileNumber, rasterNumber):
		return [z[rasterNumber] for z in self.Profiles[profileNumber][2]]



	def GetRasterName(self,idx):
		#str(self.PH.GetRasterName(k)).decode("iso-8859-1"))
		return self.Profiles[0][3][idx]



	def GetRasterMinMax(self):

		zMin=99999999
		zMax=-99999999

		for i in range(self.ProfileCount()):
			pnts = self.GetPoints(i)
			for j in range(len(pnts)):
				for k in range(self.RasterCount(i)):

					rasterVals=self.GetRasterVals(i,k)
					tmpMin=min(rasterVals)
					tmpMax=max(rasterVals)

					if tmpMin <zMin:
						zMin=tmpMin
					if tmpMax > zMax:
						zMax=tmpMax

		return zMin, zMax



	def Flip(self):

		profileCnt=self.ProfileCount()

		for i in range(profileCnt):

			#pnts
			self.Profiles[i][0].reverse()

			#distances
			self.Profiles[i][1]=self._flipDistances(self.Profiles[i][1])

			#attributes
			if self.AttributeCount(i) > 0:
				self.Profiles[i][4] = self._flipAttributes(self.Profiles[i][4])

			#rasterwerte
			#txt = open('C:/Users/bergw/_TEMP/rasterVals.txt','a')
			#txt.write(str(self.Profiles[i][2]))
			#txt.write('\r\n')
			self.Profiles[i][2].reverse()
			#txt.write(str(self.Profiles[i][2]))
			#txt.write('\r\n\r\n')
			#txt.close()

		return self.Profiles



	def _flipDistances(self, dists):

		newDists=[]
		maxD=dists[-1]
		for dOld in dists:
			newDists.append((dOld-maxD)*float(-1))

		newDists.reverse()
		return newDists



	def _flipAttributes(self, attributes):

		items=attributes.items()
		items.reverse()
		od = collections.OrderedDict(items)

		return od


