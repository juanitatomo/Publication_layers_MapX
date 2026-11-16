<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>K1-KAPOS</sld:Name>
    <sld:UserStyle>
      <sld:Name>K1-KAPOS</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>grid</ogc:PropertyName>
            </sld:Geometry>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#FFFFFF" opacity="0" quantity="0" label=""/>
              <sld:ColorMapEntry color="#d5f7f3" opacity="1.0" quantity="1" label="Kapos class 1  &gt; 4500m "/>
              <sld:ColorMapEntry color="#bcebd9" opacity="1.0" quantity="2" label="Kapos class 2  3500m - 4500m"/>
              <sld:ColorMapEntry color="#5cbd7d" opacity="1.0" quantity="3" label="Kapos class 3  2500m - 3500m"/>
              <sld:ColorMapEntry color="#8bc775" opacity="1.0" quantity="4" label="Kapos class 4  1500m - 2500m slope &gt; 2 deg"/>
              <sld:ColorMapEntry color="#62803b" opacity="1.0" quantity="5" label="Kapos  class5  1000m - 1500m slope &gt; 5 deg or LER &gt; 300m"/>
              <sld:ColorMapEntry color="#ada957" opacity="1.0" quantity="6" label="Kapos class6  300m - 1000m &amp; LER &gt; 300m"/>
              <sld:ColorMapEntry color="#bd9a59" opacity="1.0" quantity="7" label="Kapos class 7 isolated inner basins/plateau &lt; 25km2"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>