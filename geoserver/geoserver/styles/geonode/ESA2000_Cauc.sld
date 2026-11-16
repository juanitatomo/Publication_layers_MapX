<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.0.0" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>Landcover categories</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry quantity="10" label="Cropland, rainfed" color="#ffff64"/>
              <sld:ColorMapEntry quantity="20" label="Cropland, irrigated or post‐flooding" color="#aaf0f0"/>
              <sld:ColorMapEntry quantity="30" label="Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (&lt;50%)" color="#dcf064"/>
              <sld:ColorMapEntry quantity="40" label="Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (&lt;50%) " color="#c7c764"/>
              <sld:ColorMapEntry quantity="50" label="Tree cover, broadleaved, evergreen, closed to open (>15%)" color="#006400"/>
              <sld:ColorMapEntry quantity="60" label="Tree cover, broadleaved, deciduous, closed to open (>15%)" color="#009f00"/>
              <sld:ColorMapEntry quantity="70" label="Tree cover, needleleaved, evergreen, closed to open (>15%)" color="#003b00"/>
              <sld:ColorMapEntry quantity="80" label="Tree cover, needleleaved, deciduous, closed to open (>15%)" color="#275000"/>
              <sld:ColorMapEntry quantity="90" label="Tree cover, mixed leaf type (broadleaved and needleleaved)" color="#788300"/>
              <sld:ColorMapEntry quantity="100" label="Mosaic tree and shrub (>50%) / herbaceous cover (&lt;50%)" color="#8c9f00"/>
              <sld:ColorMapEntry quantity="110" label="Mosaic herbaceous cover (>50%) / tree and shrub (&lt;50%)" color="#be9600"/>
              <sld:ColorMapEntry quantity="120" label="Shrubland" color="#966400"/>
              <sld:ColorMapEntry quantity="130" label="Grassland" color="#ffb332"/>
              <sld:ColorMapEntry quantity="140" label="Lichens and mosses" color="#ffdcd2"/>
              <sld:ColorMapEntry quantity="150" label="Sparse vegetation (tree, shrub, herbaceous cover) (&lt;15%)" color="#ffd278"/>
              <sld:ColorMapEntry quantity="160" label="Tree cover, flooded, fresh or brakish water" color="#007859"/>
              <sld:ColorMapEntry quantity="170" label="Tree cover, flooded, saline water" color="#009678"/>
              <sld:ColorMapEntry quantity="180" label="Shrub or herbaceous cover, flooded, fresh/saline/brakish water" color="#00dc83"/>
              <sld:ColorMapEntry quantity="190" label="Urban areas" color="#c31300"/>
              <sld:ColorMapEntry quantity="200" label="Bare areas" color="#fff4d7"/>
              <sld:ColorMapEntry quantity="210" label="Water bodies" color="#0046c7"/>
              <sld:ColorMapEntry quantity="220" label="Permanent snow and ice" color="#ffffff"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>