rm -Rf dist/
python setup.py py2app
cp __boot__.py dist/Moonstone.app/Contents/Resources/
#cp /usr/lib/libpyside-python2.7.* dist/Moonstone.app/Contents/Frameworks/
#cp /usr/lib/libshiboken-python2.7.* dist/Moonstone.app/Contents/Frameworks/
#cp /usr/lib/libstdc++.6.dylib dist/Moonstone.app/Contents/Frameworks/
#mv dist/Moonstone.app/Contents/Frameworks/Qt* dist/Moonstone.app/Contents/Frameworks/
touch ./dist/Moonstone.app/Contents/Resources/qt.conf
